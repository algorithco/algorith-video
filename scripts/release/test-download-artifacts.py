#!/usr/bin/env python3
"""Tiny mocked artifact downloads; no GitHub access or application builds."""
import hashlib
import importlib.util
import io
import json
import stat
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock
import zipfile

SPEC = importlib.util.spec_from_file_location("release_artifact_downloader", Path(__file__).with_name("download-artifacts.py"))
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


def zip_bytes(entries):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as bundle:
        for name, data in entries:
            bundle.writestr(name, data)
    return output.getvalue()


def artifact(name, identifier, content, **changes):
    return {"id": identifier, "name": name, "expired": False, "workflow_run": {"id": 123},
            "size_in_bytes": len(content), "digest": f"sha256:{hashlib.sha256(content).hexdigest()}", **changes}


class DownloadTests(unittest.TestCase):
    def setUp(self):
        workspace = Path.cwd().resolve()
        self.temporary = tempfile.TemporaryDirectory(prefix="_artifact-download-fixture-", dir=workspace)
        self.root = Path(self.temporary.name).resolve()
        self.assertTrue(self.root.is_relative_to(workspace) and self.root != workspace)
        self.addCleanup(self.temporary.cleanup)
        self.environment = {"GH_TOKEN": "fixture-secret-token", "GITHUB_API_URL": "https://api.github.test",
                            "GITHUB_REPOSITORY": "fixture/project", "GITHUB_RUN_ID": "123"}
        self.api_requests, self.blob_requests = [], []
        self.addCleanup(mock.patch.stopall)
        mock.patch.object(HELPER.time, "sleep").start()
        mock.patch("builtins.print").start()

    def transport(self, pages, contents):
        def api_open(request, timeout):
            self.api_requests.append(request)
            self.assertEqual(request.get_header("Authorization"), "Bearer fixture-secret-token")
            if "/artifacts?" in request.full_url:
                page = int(request.full_url.rsplit("page=", 1)[1])
                return io.BytesIO(json.dumps({"artifacts": pages[page - 1]}).encode())
            identifier = request.full_url.rsplit("/", 2)[1]
            raise urllib.error.HTTPError(request.full_url, 302, "Found",
                                         {"Location": f"https://blob.example.test/{identifier}?signature=fixture-private-signature"}, None)

        def blob_open(request, timeout):
            self.blob_requests.append(request)
            self.assertIsNone(request.get_header("Authorization"))
            identifier = request.full_url.split("/", 3)[3].split("?", 1)[0]
            content = contents[identifier]
            if isinstance(content, list):
                content = content.pop(0)
            if isinstance(content, Exception):
                raise content
            return io.BytesIO(content)

        mock.patch.object(HELPER.API_OPENER, "open", side_effect=api_open).start()
        mock.patch.object(HELPER.urllib.request, "urlopen", side_effect=blob_open).start()

    def test_named_download_and_redirect_does_not_forward_token(self):
        content = zip_bytes([("source-manifest.json", "{}"), ("licenses/LICENSE", "Fixture license")])
        metadata = artifact("media-sources", 1, content, size_in_bytes=999999)
        self.transport([[metadata]], {"1": content})
        destination = self.root / "media-sources"
        HELPER.download(destination, "media-sources", self.environment)
        self.assertEqual((destination / "source-manifest.json").read_text(), "{}")
        self.assertEqual((destination / "licenses/LICENSE").read_text(), "Fixture license")
        self.assertEqual(list(self.root.iterdir()), [destination])
        self.assertEqual(len(self.blob_requests), 1)
        request = HELPER.api_request("https://api.github.test/artifact", "fixture-secret-token")
        self.assertIsNone(HELPER.NoRedirect().redirect_request(request, None, 302, "Found", {}, "https://blob.example.test"))

    def test_pagination_latest_nonexpired_and_publisher_folders(self):
        old = zip_bytes([("old", "old")])
        new = zip_bytes([("source-manifest.json", "new")])
        windows = zip_bytes([("installer.exe", "tiny fixture")])
        first = artifact("media-sources", 1, old)
        second = artifact("media-sources", 2, new)
        expired = artifact("media-sources", 9, old, expired=True)
        other = artifact("windows-x64", 3, windows)
        self.transport([[first] * 100, [second, expired, other]], {"2": new, "3": windows})
        destination = self.root / "release-inputs"
        result = HELPER.download(destination, environment=self.environment)
        self.assertEqual([item["id"] for item in result], [2, 3])
        self.assertEqual((destination / "media-sources/source-manifest.json").read_text(), "new")
        self.assertTrue((destination / "windows-x64/installer.exe").is_file())

    def test_incomplete_stream_retries_then_succeeds(self):
        content = zip_bytes([("manifest", "complete")])
        self.transport([[artifact("media-sources", 1, content)]], {"1": [content[:20], IOError("network fixture"), content]})
        HELPER.download(self.root / "result", "media-sources", self.environment)
        self.assertEqual(len(self.blob_requests), 3)
        self.assertEqual((self.root / "result/manifest").read_text(), "complete")

    def test_hash_failure_is_closed_and_cleans_temporary_files(self):
        expected = zip_bytes([("manifest", "expected")])
        self.transport([[artifact("media-sources", 1, expected)]], {"1": b"partial download"})
        with self.assertRaises(HELPER.ArtifactError) as caught:
            HELPER.download(self.root / "result", "media-sources", self.environment)
        self.assertEqual(len(self.blob_requests), 3)
        self.assertNotIn("fixture-secret", str(caught.exception))
        self.assertNotIn("signature", str(caught.exception))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_zip_crc_failure_even_with_matching_zip_digest(self):
        content = zip_bytes([("manifest", "unique CRC fixture content")])
        corrupted = content.replace(b"unique CRC fixture content", b"Unique CRC fixture content", 1)
        self.transport([[artifact("media-sources", 1, corrupted)]], {"1": corrupted})
        with self.assertRaises(HELPER.ArtifactError):
            HELPER.download(self.root / "result", "media-sources", self.environment)
        self.assertEqual(len(self.blob_requests), 3)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_unsafe_zip_members_are_rejected_before_extraction(self):
        link = zipfile.ZipInfo("link")
        link.create_system = 3
        link.external_attr = (stat.S_IFLNK | 0o777) << 16
        fixtures = [[("../escape", "bad")], [("/absolute", "bad")], [("C:/escape", "bad")],
                    [("dir\\escape", "bad")], [("CON", "bad")], [("a", "one"), ("A", "two")],
                    [("file", "one"), ("file/child", "two")], [(link, "target")]]
        for index, entries in enumerate(fixtures):
            with self.subTest(index=index):
                archive = self.root / f"unsafe-{index}.zip"
                content = zip_bytes(entries)
                if index == 3:
                    # ZipInfo normalizes backslashes when creating archives on
                    # Windows; emulate a stored, untrusted ZIP path directly.
                    content = content.replace(b"dir/escape", b"dir\\escape")
                archive.write_bytes(content)
                with self.assertRaises(HELPER.ArtifactError):
                    HELPER.extract_zip(archive, self.root / f"unsafe-{index}")
                self.assertFalse((self.root / f"unsafe-{index}").exists())

    def test_required_digest_and_trusted_run_identity(self):
        content = zip_bytes([("manifest", "fixture")])
        self.transport([[artifact("media-sources", 1, content, digest=None)]], {"1": content})
        with self.assertRaisesRegex(HELPER.ArtifactError, "mandatory SHA-256"):
            HELPER.download(self.root / "result", "media-sources", self.environment)
        with self.assertRaises(HELPER.ArtifactError):
            HELPER.identity({**self.environment, "GITHUB_RUN_ID": "../other"})
        with self.assertRaises(HELPER.ArtifactError):
            HELPER.identity({**self.environment, "GITHUB_API_URL": "http://api.github.test"})
        response = io.BytesIO(json.dumps({"artifacts": [artifact("media-sources", 1, content, workflow_run={"id": 124})]}).encode())
        with mock.patch.object(HELPER.API_OPENER, "open", return_value=response):
            with self.assertRaisesRegex(HELPER.ArtifactError, "metadata"):
                HELPER.download(self.root / "result", "media-sources", self.environment)
        self.assertEqual(self.blob_requests, [])

    def test_publisher_commits_output_only_after_every_artifact_verifies(self):
        first = zip_bytes([("good", "fixture")])
        second = zip_bytes([("bad", "expected")])
        self.transport([[artifact("a-sources", 1, first), artifact("b-windows", 2, second)]],
                       {"1": first, "2": b"truncated"})
        with self.assertRaises(HELPER.ArtifactError):
            HELPER.download(self.root / "release-inputs", environment=self.environment)
        self.assertEqual(list(self.root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
