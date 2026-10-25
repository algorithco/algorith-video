#!/usr/bin/env python3
"""Collect the pinned Windows/Linux media sources on a GitHub Linux runner.

The upstream download-only helper obtains the dependency source snapshots used
by the pinned recipes, including their special submodule and Cargo vendoring
steps. No FFmpeg or installer compilation is performed here. The source bundle
is a superset: it also contains recipes/sources for disabled upstream variants.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
RECIPES_REPOSITORY = "https://github.com/BtbN/FFmpeg-Builds.git"
FFMPEG_REPOSITORY = "https://github.com/FFmpeg/FFmpeg.git"
MAX_RELEASE_ASSET_BYTES = 2_000_000_000
NOTICE_NAME = re.compile(r"^(licen[sc]e|copying|copyright|notice|unlicen[sc]e)(?:[._-]|$)", re.I)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(command, cwd=None, env=None, timeout=1800):
    subprocess.run(command, cwd=cwd, env=env, check=True, timeout=timeout)


def clone_commit(repository, commit, destination):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise RuntimeError("A full immutable source commit is required")
    run(["git", "init", str(destination)])
    run(["git", "-C", str(destination), "remote", "add", "origin", repository])
    run(["git", "-C", str(destination), "fetch", "--depth=1", "origin", commit])
    run(["git", "-C", str(destination), "checkout", "--detach", "FETCH_HEAD"])
    actual = subprocess.check_output(["git", "-C", str(destination), "rev-parse", "HEAD"], text=True).strip()
    if actual != commit:
        raise RuntimeError("Source checkout does not match the release pin")


def source_files(directory):
    for current, directories, files in os.walk(directory):
        directories[:] = sorted(name for name in directories if name not in {".git", ".cache"})
        for name in sorted(files):
            path = Path(current) / name
            if not path.is_symlink() and path.is_file():
                yield path


def collect_notice(output, component, original_name, content, notices):
    if not content or b"\0" in content:
        return
    checksum = hashlib.sha256(content).hexdigest()
    # Flatten long vendored paths for Windows extraction, while retaining the
    # original source path and full digest in the index.
    basename = re.sub(r'[^A-Za-z0-9._-]', "_", PurePosixPath(original_name).name)[:70]
    relative = f"THIRD_PARTY_LICENSES/{component}/{checksum[:16]}-{basename}"
    destination = output / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        destination.write_bytes(content)
    notices.append({"path": relative, "source_path": original_name, "component": component,
                    "size": len(content), "sha256": checksum})


def collect_tree_notices(output, directory, component, notices):
    for path in source_files(directory):
        if NOTICE_NAME.match(path.name) and path.stat().st_size <= 2 * 1024 * 1024:
            collect_notice(output, component, path.relative_to(directory).as_posix(), path.read_bytes(), notices)


def collect_cached_notices(output, archive, component, notices):
    with tarfile.open(archive, "r:*") as source:
        for member in source:
            parts = PurePosixPath(member.name).parts
            if (not member.isfile() or ".git" in parts or member.size > 2 * 1024 * 1024
                    or not NOTICE_NAME.match(PurePosixPath(member.name).name)):
                continue
            stream = source.extractfile(member)
            if stream is not None:
                with stream:
                    collect_notice(output, component, member.name, stream.read(), notices)


def stage(output):
    if sys.platform != "linux" or os.environ.get("GITHUB_ACTIONS") != "true":
        raise RuntimeError("Collect release media sources on a GitHub Actions Linux runner")
    output = Path(output).resolve()
    if output.exists() and any(output.iterdir()):
        raise RuntimeError("Use an empty media source artifact directory")
    output.mkdir(parents=True, exist_ok=True)
    lock = json.loads((ROOT / "scripts/release/runtime-lock.json").read_text())
    recipe_commit = lock["ffmpeg"]["build_commit"]
    ffmpeg_commit = lock["ffmpeg"]["source_commit"]
    for platform in ("windows", "linux"):
        if lock["ffmpeg"][platform].get("build_commit", recipe_commit) != recipe_commit:
            raise RuntimeError("One source bundle cannot describe different media recipes")
    with tempfile.TemporaryDirectory(prefix="algorithvideo-media-sources-") as temporary:
        work = Path(temporary)
        recipes, ffmpeg = work / "recipes", work / "FFmpeg"
        clone_commit(RECIPES_REPOSITORY, recipe_commit, recipes)
        clone_commit(FFMPEG_REPOSITORY, ffmpeg_commit, ffmpeg)
        environment = {**os.environ, "GITHUB_REPOSITORY": "BtbN/FFmpeg-Builds"}
        # This upstream script only downloads immutable dependency sources.
        # Its base image supplies git/download/cargo tools, not app artifacts.
        run(["bash", "download.sh"], cwd=recipes, env=environment, timeout=5400)
        sources = sorted(path for path in (recipes / ".cache/downloads").glob("*.tar.xz")
                         if path.is_file() and not path.is_symlink())
        if not sources:
            raise RuntimeError("The upstream source download produced no dependency snapshots")
        notices, index_files = [], []
        collect_tree_notices(output, recipes, "build-recipes", notices)
        collect_tree_notices(output, ffmpeg, "FFmpeg", notices)
        for archive in sources:
            component = re.sub(r"_[a-f0-9]{64}$", "", archive.name.removesuffix(".tar.xz"))
            if not re.fullmatch(r"[A-Za-z0-9._-]+", component):
                raise RuntimeError("Unexpected source cache component name")
            collect_cached_notices(output, archive, component, notices)
            index_files.append({"path": f"dependency-sources/{archive.name}",
                                "size": archive.stat().st_size, "sha256": digest(archive)})
        for directory, label in ((recipes, "build-recipes"), (ffmpeg, "FFmpeg")):
            for path in source_files(directory):
                index_files.append({"path": f"{label}/{path.relative_to(directory).as_posix()}",
                                    "size": path.stat().st_size, "sha256": digest(path)})
        index = {"schema": 1, "recipe_repository": RECIPES_REPOSITORY, "recipe_commit": recipe_commit,
                 "ffmpeg_repository": FFMPEG_REPOSITORY, "ffmpeg_commit": ffmpeg_commit,
                 "dependency_sources": "All source snapshots from the pinned upstream download-only recipes; includes disabled variants.",
                 "files": index_files, "notices": notices}
        index_path = work / "source-index.json"
        write_json(index_path, index)
        archive = output / "ffmpeg-sources-windows-linux.tar.gz"
        with tarfile.open(archive, "w:gz", compresslevel=1) as bundle:
            for directory, label in ((recipes, "build-recipes"), (ffmpeg, "FFmpeg")):
                for path in source_files(directory):
                    bundle.add(path, arcname=f"{label}/{path.relative_to(directory).as_posix()}", recursive=False)
            for source in sources:
                bundle.add(source, arcname=f"dependency-sources/{source.name}", recursive=False)
            bundle.add(output / "THIRD_PARTY_LICENSES", arcname="THIRD_PARTY_LICENSES")
            bundle.add(index_path, arcname="source-index.json")
        if archive.stat().st_size >= MAX_RELEASE_ASSET_BYTES:
            raise RuntimeError("Source archive exceeds the release asset limit; split it before publication")
        manifest = {"schema": 1, "recipe_commit": recipe_commit, "ffmpeg_commit": ffmpeg_commit,
                    "recipe_repository": RECIPES_REPOSITORY, "ffmpeg_repository": FFMPEG_REPOSITORY,
                    "archive": {"name": archive.name, "size": archive.stat().st_size, "sha256": digest(archive)},
                    "source_index_sha256": digest(index_path), "notices": notices}
        write_json(output / "source-manifest.json", manifest)
    print(json.dumps({"archive": manifest["archive"], "dependency_snapshots": len(sources),
                      "notice_files": len({notice["path"] for notice in notices})}), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="media-sources")
    stage(parser.parse_args().output)
