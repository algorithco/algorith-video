#!/usr/bin/env python3
"""Stream and verify both macOS corresponding-source archives without extraction."""
import argparse
import hashlib
import json
import re
import sys
import tarfile
from pathlib import Path


class SourceValidationError(ValueError):
    pass


def safe_path(name):
    if (not isinstance(name, str) or not name or "\\" in name or ":" in name
            or any(part in ("", ".", "..") for part in name.split("/"))
            or any(ord(character) < 32 for character in name)):
        raise SourceValidationError("Unsafe source archive path")
    return name


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise SourceValidationError("Duplicate source manifest key")
        value[key] = item
    return value


def verify_archive(archive, platform, source_sha):
    if platform not in ("mac-arm64", "mac-x64") or not re.fullmatch(r"[a-f0-9]{40}", source_sha):
        raise SourceValidationError("Invalid expected macOS source identity")
    archive = Path(archive)
    if archive.is_symlink() or not archive.is_file():
        raise SourceValidationError(f"Missing regular {platform} source archive")
    prefix = f"ffmpeg-sources-{platform}"
    manifest_name = f"{prefix}/source-manifest.json"
    seen, directories, actual = set(), set(), {}
    manifest = None
    try:
        with tarfile.open(archive, "r|gz") as bundle:
            for member in bundle:
                name = member.name[:-1] if member.name.endswith("/") else member.name
                safe_path(name)
                if name != prefix and not name.startswith(prefix + "/"):
                    raise SourceValidationError("Source member is outside its platform directory")
                if name in seen:
                    raise SourceValidationError("Duplicate source archive member")
                seen.add(name)
                if member.isdir():
                    directories.add(name)
                    continue
                if not member.isfile() or member.issparse() or name == prefix:
                    raise SourceValidationError("Source archive contains a link or non-regular payload")
                stream = bundle.extractfile(member)
                if stream is None:
                    raise SourceValidationError("Unreadable source archive payload")
                with stream:
                    if name == manifest_name:
                        if member.size > 4 * 1024 * 1024:
                            raise SourceValidationError("Source manifest is too large")
                        manifest = json.loads(stream.read(), object_pairs_hook=unique_object)
                    else:
                        checksum, size = hashlib.sha256(), 0
                        while block := stream.read(1024 * 1024):
                            checksum.update(block)
                            size += len(block)
                        if size != member.size:
                            raise SourceValidationError("Truncated source archive payload")
                        actual[name[len(prefix) + 1:]] = (size, checksum.hexdigest())
    except (tarfile.TarError, EOFError, OSError, UnicodeError, json.JSONDecodeError) as error:
        raise SourceValidationError(f"Invalid {platform} source archive: {error}") from None
    if (not isinstance(manifest, dict) or manifest.get("product") != "AlgorithVideo"
            or manifest.get("platform") != platform or manifest.get("source_sha") != source_sha):
        raise SourceValidationError(f"Wrong {platform} source manifest identity")
    entries = manifest.get("files")
    if not isinstance(entries, list) or not entries:
        raise SourceValidationError("Missing source manifest payload list")
    expected = {}
    expected_directories = {prefix}
    for entry in entries:
        if not isinstance(entry, dict):
            raise SourceValidationError("Invalid source manifest payload")
        name = safe_path(entry.get("path"))
        size, checksum = entry.get("size"), entry.get("sha256")
        if (name == "source-manifest.json" or name in expected or type(size) is not int or size < 0
                or not isinstance(checksum, str) or not re.fullmatch(r"[a-f0-9]{64}", checksum)):
            raise SourceValidationError("Invalid or duplicate source manifest payload")
        expected[name] = (size, checksum)
        components = name.split("/")
        expected_directories.update(prefix + "/" + "/".join(components[:index]) for index in range(1, len(components)))
    if actual != expected:
        raise SourceValidationError(f"{platform} source payload set, size or SHA-256 mismatch")
    if not directories.issubset(expected_directories):
        raise SourceValidationError("Source archive contains an undeclared directory")
    for name in actual:
        components = name.split("/")
        if any("/".join(components[:index]) in actual for index in range(1, len(components))):
            raise SourceValidationError("Conflicting source file and directory paths")
    return len(actual)


def verify(root, source_sha):
    root = Path(root).resolve()
    for platform in ("mac-arm64", "mac-x64"):
        directory = root / platform
        if directory.is_symlink() or not directory.is_dir():
            raise SourceValidationError(f"Missing regular {platform} artifact directory")
        count = verify_archive(directory / f"ffmpeg-sources-{platform}.tar.gz", platform, source_sha)
        print(f"Verified {platform} corresponding sources: {count} payload files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--source-sha", required=True)
    arguments = parser.parse_args()
    try:
        verify(arguments.root, arguments.source_sha)
    except SourceValidationError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
