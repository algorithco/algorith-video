#!/usr/bin/env python3
"""Stage relocatable Windows/Linux tools; all network archives are hash locked."""
import hashlib
import json
import os
import platform
import re
import runpy
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]


def source_file(directory, relative):
    if (not isinstance(relative, str) or "\\" in relative
            or PurePosixPath(relative).is_absolute() or ".." in PurePosixPath(relative).parts):
        raise RuntimeError("Invalid media source artifact path")
    path = directory / relative
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(directory):
        raise RuntimeError("Missing or unsafe media source artifact")
    return path


def file_digest(path):
    with path.open("rb") as content:
        return hashlib.file_digest(content, "sha256").hexdigest()


def verified_media_sources(lock):
    requested = os.environ.get("ALGORITHVIDEO_MEDIA_SOURCES_DIR")
    if not requested:
        if os.environ.get("GITHUB_ACTIONS") == "true":
            raise RuntimeError("Release staging requires ALGORITHVIDEO_MEDIA_SOURCES_DIR")
        return None
    directory = Path(requested).resolve()
    manifest_path = source_file(directory, "source-manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (manifest.get("schema") != 1 or manifest.get("recipe_commit") != lock["ffmpeg"]["build_commit"]
            or manifest.get("ffmpeg_commit") != lock["ffmpeg"]["source_commit"]):
        raise RuntimeError("Media source manifest does not match the runtime recipe/source pins")
    archive = manifest.get("archive", {})
    name, checksum, size = archive.get("name"), archive.get("sha256"), archive.get("size")
    if (not isinstance(name, str) or "/" in name or "\\" in name
            or not name.startswith("ffmpeg-sources-windows-linux.tar.")
            or not isinstance(checksum, str) or not re.fullmatch(r"[a-f0-9]{64}", checksum)
            or not isinstance(size, int) or isinstance(size, bool) or size <= 0):
        raise RuntimeError("Invalid corresponding-source archive record")
    source = source_file(directory, name)
    if source.stat().st_size != size or file_digest(source) != checksum:
        raise RuntimeError("Corresponding-source archive size or checksum mismatch")
    notices = manifest.get("notices")
    if not isinstance(notices, list) or not notices:
        raise RuntimeError("Corresponding-source license inventory is missing")
    notice_files = {}
    for notice in notices:
        relative = notice.get("path", "")
        if not relative.startswith("THIRD_PARTY_LICENSES/"):
            raise RuntimeError("Invalid corresponding-source license path")
        path = source_file(directory, relative)
        if path.stat().st_size != notice.get("size") or file_digest(path) != notice.get("sha256"):
            raise RuntimeError("Corresponding-source license checksum mismatch")
        notice_files[relative] = path
    return manifest_path, manifest, notice_files


def download(url, destination, digest):
    with urllib.request.urlopen(url, timeout=120) as response, destination.open("wb") as out:
        shutil.copyfileobj(response, out)
    with destination.open("rb") as content:
        actual = hashlib.file_digest(content, "sha256").hexdigest()
    if actual != digest:
        raise RuntimeError(f"Checksum mismatch: {destination.name}")


def extract(archive, destination):
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as bundle:
            for item in bundle.infolist():
                candidate = (destination / item.filename).resolve()
                if not candidate.is_relative_to(destination.resolve()):
                    raise RuntimeError("Unsafe archive member")
            bundle.extractall(destination)
    else:
        with tarfile.open(archive) as bundle:
            bundle.extractall(destination, filter="data")


def stage():
    target = {"win32": "windows", "linux": "linux"}.get(sys.platform)
    if target is None or platform.machine().lower() not in ("amd64", "x86_64"):
        raise RuntimeError("Use a native x64 Windows or Linux runner")
    lock = json.loads((ROOT / "scripts/release/runtime-lock.json").read_text())
    media_sources = verified_media_sources(lock)
    venv, binaries = ROOT / "engine-venv", ROOT / "engine-bin"
    if venv.exists() or binaries.exists():
        raise RuntimeError("Runtime directories already exist; use a clean checkout")
    with tempfile.TemporaryDirectory(prefix="algorithvideo-runtime-") as scratch:
        work = Path(scratch)
        py = lock["python"]
        filename = f'cpython-{py["version"]}+{py["tag"]}-{py[target]["target"]}-install_only_stripped.tar.gz'
        archive = work / filename
        download(f'https://github.com/astral-sh/python-build-standalone/releases/download/{py["tag"]}/{filename}', archive, py[target]["sha256"])
        extract(archive, work / "python-extract")
        shutil.copytree(work / "python-extract/python", venv, symlinks=False)
        interpreter = venv / ("python.exe" if target == "windows" else "bin/python3")
        subprocess.run([str(interpreter), "-m", "pip", "install", "--no-compile", "--require-hashes", "-r", str(ROOT / "engine/requirements.lock")], check=True)
        download(f'https://raw.githubusercontent.com/python/cpython/v{py["version"]}/LICENSE', venv / "PYTHON-LICENSE", "3b2f81fe21d181c499c59a256c8e1968455d6689d269aa85373bfb6af41da3bf")
        if target == "windows":
            # pip's console EXEs retain the runner's absolute interpreter path.
            # The desktop invokes modules through python.exe and its own native
            # yt-dlp launcher; unused absolute-path wrappers must not ship.
            helpers = runpy.run_path(
                str(ROOT / "scripts/release/stage-python-runtime.py"),
                run_name="algorithvideo_python_staging_helpers",
            )
            helpers["remove_console_wrappers"](venv)
        ff = lock["ffmpeg"]
        spec = ff[target]
        archive = work / spec["file"]
        # A maintainer may mirror the exact upstream archives for long-term
        # retention. The committed digest remains mandatory for mirrors.
        tag = spec.get("tag", ff["tag"])
        base = os.environ.get("ALGORITHVIDEO_FFMPEG_MIRROR") or f'https://github.com/BtbN/FFmpeg-Builds/releases/download/{tag}'
        if not base.startswith("https://"):
            raise RuntimeError("Archive mirror must use HTTPS")
        cached = os.environ.get("ALGORITHVIDEO_FFMPEG_ARCHIVE")
        if cached:
            shutil.copy2(cached, archive)
            with archive.open("rb") as content:
                if hashlib.file_digest(content, "sha256").hexdigest() != ff[target]["sha256"]:
                    raise RuntimeError("Mirrored FFmpeg checksum mismatch")
        else:
            download(f'{base}/{archive.name}', archive, ff[target]["sha256"])
        extract(archive, work / "ffmpeg")
        distribution, = (work / "ffmpeg").iterdir()
        shutil.copytree(distribution / "bin", binaries, symlinks=False)
        if target == "linux":
            shutil.copytree(distribution / "lib", binaries / "lib", symlinks=False)
            # Keep every loader path inside this relocatable media directory.
            for binary in [binaries / "ffmpeg", binaries / "ffprobe", *list((binaries / "lib").glob("*.so*"))]:
                if binary.is_file():
                    subprocess.run(["patchelf", "--set-rpath", "$ORIGIN:$ORIGIN/lib", str(binary)], check=True)
        (binaries / ("ffplay.exe" if target == "windows" else "ffplay")).unlink(missing_ok=True)
        shutil.copy2(distribution / "LICENSE.txt", binaries / "FFMPEG-LICENSE")
        shutil.copy2(ROOT / "scripts/release/runtime-lock.json", binaries / "RUNTIME-PROVENANCE.json")
        (binaries / "FFMPEG-SOURCE.txt").write_text(
            f'FFmpeg {spec.get("version", "8.1.3")}, LGPL shared build. Build recipes and dependency revisions:\n'
            f'https://github.com/BtbN/FFmpeg-Builds/tree/{spec.get("build_commit", ff["build_commit"])}\n'
            f'FFmpeg source commit: {ff["source_commit"]}\n'
            + ('Corresponding sources were verified against the release source manifest.\n' if media_sources
               else 'Publication requires the matching corresponding-source archive and dependency notices.\n'), encoding="utf-8")
        if media_sources:
            manifest_path, manifest, notice_files = media_sources
            shutil.copy2(manifest_path, binaries / "FFMPEG-SOURCE-MANIFEST.json")
            for relative, source in notice_files.items():
                destination = binaries / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            version = json.loads((ROOT / "package.json").read_text())["version"]
            with (binaries / "FFMPEG-SOURCE.txt").open("a", encoding="utf-8") as description:
                description.write(
                    f'Corresponding source archive: https://github.com/algorithco/algorith-video/releases/download/v{version}/{manifest["archive"]["name"]}\n'
                    f'Source archive SHA-256: {manifest["archive"]["sha256"]}\n'
                    'The source bundle and license inventory also include disabled upstream variants.\n')
        if target == "windows":
            subprocess.run(["powershell", "-NoProfile", "-File", str(ROOT / "scripts/release/build-launcher.ps1")], check=True)
        else:
            launcher = binaries / "yt-dlp"
            launcher.write_text('#!/bin/sh\nBUNDLE_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)\nexec "$BUNDLE_DIR/../engine-venv/bin/python3" -P -m yt_dlp "$@"\n')
            launcher.chmod(0o755)
        for cache in venv.rglob("__pycache__"):
            shutil.rmtree(cache)
        version = subprocess.check_output([str(binaries / ("ffmpeg.exe" if target == "windows" else "ffmpeg")), "-version"], text=True)
        if "--enable-gpl" in version or "--enable-nonfree" in version or "--enable-libopenh264" not in version:
            raise RuntimeError("Unexpected media build license or missing CPU H.264 encoder")
        (binaries / "FFMPEG-CONFIGURATION.txt").write_text(version, encoding="utf-8")
    print(f"Staged verified {target} x64 runtime")


if __name__ == "__main__":
    stage()
