#!/usr/bin/env python3
"""Small synthetic source archives; no downloads, extraction or app builds."""
import hashlib
import importlib.util
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("verify_mac_sources", Path(__file__).with_name("verify-mac-sources.py"))
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)
SHA = "a" * 40


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="_mac-source-fixture-", dir=Path.cwd())
        self.root = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def archive(self, platform="mac-arm64", *, source_sha=SHA, declared_platform=None,
                corrupt=False, wrong_size=False, extra=None, duplicate=False, link=False, missing=False):
        directory = self.root / platform
        directory.mkdir(exist_ok=True)
        archive = directory / f"ffmpeg-sources-{platform}.tar.gz"
        prefix = f"ffmpeg-sources-{platform}"
        data = b"tiny corresponding source\n"
        manifest = {"product": "AlgorithVideo", "platform": declared_platform or platform, "source_sha": source_sha,
                    "files": [{"path": "homebrew/libass/source.tar.xz", "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}]}
        if wrong_size:
            manifest["files"][0]["size"] += 1
        with tarfile.open(archive, "w:gz") as bundle:
            def add(name, content):
                item = tarfile.TarInfo(name)
                item.size = len(content)
                bundle.addfile(item, io.BytesIO(content))
            if not missing:
                add(f"{prefix}/homebrew/libass/source.tar.xz", b"x" * len(data) if corrupt else data)
            if duplicate:
                add(f"{prefix}/homebrew/libass/source.tar.xz", data)
            if extra:
                add(extra, b"unexpected")
            if link:
                item = tarfile.TarInfo(f"{prefix}/external")
                item.type, item.linkname = tarfile.SYMTYPE, "/outside"
                bundle.addfile(item)
            add(f"{prefix}/source-manifest.json", json.dumps(manifest).encode())
        return archive

    def test_both_architectures_and_revision_pass(self):
        self.archive()
        self.archive("mac-x64")
        HELPER.verify(self.root, SHA)

    def test_corrupt_payload_rejected(self):
        with self.assertRaises(HELPER.SourceValidationError):
            HELPER.verify_archive(self.archive(corrupt=True), "mac-arm64", SHA)

    def test_wrong_payload_size_rejected(self):
        with self.assertRaises(HELPER.SourceValidationError):
            HELPER.verify_archive(self.archive(wrong_size=True), "mac-arm64", SHA)

    def test_wrong_revision_rejected(self):
        with self.assertRaises(HELPER.SourceValidationError):
            HELPER.verify_archive(self.archive(source_sha="b" * 40), "mac-arm64", SHA)

    def test_wrong_architecture_rejected(self):
        with self.assertRaises(HELPER.SourceValidationError):
            HELPER.verify_archive(self.archive(declared_platform="mac-x64"), "mac-arm64", SHA)

    def test_duplicate_link_and_missing_payload_rejected(self):
        for change in ({"duplicate": True}, {"link": True}, {"missing": True}):
            with self.subTest(change=change), self.assertRaises(HELPER.SourceValidationError):
                HELPER.verify_archive(self.archive(**change), "mac-arm64", SHA)

    def test_extra_and_external_paths_rejected(self):
        for path in ("ffmpeg-sources-mac-arm64/extra", "ffmpeg-sources-mac-arm64/../escape", "/outside", "ffmpeg-sources-mac-x64/other"):
            with self.subTest(path=path), self.assertRaises(HELPER.SourceValidationError):
                HELPER.verify_archive(self.archive(extra=path), "mac-arm64", SHA)

    def test_incomplete_target_set_rejected(self):
        self.archive()
        with self.assertRaises(HELPER.SourceValidationError):
            HELPER.verify(self.root, SHA)


if __name__ == "__main__":
    unittest.main()
