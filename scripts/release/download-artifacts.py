#!/usr/bin/env python3
"""Download this run's artifacts with complete-stream and safe ZIP verification."""
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

USER_AGENT = "AlgorithVideo-release-artifacts/1"
ATTEMPTS = 3


class ArtifactError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    # An authenticated API request must never forward its token to blob storage.
    def redirect_request(self, request, fp, code, message, headers, newurl):
        return None


API_OPENER = urllib.request.build_opener(NoRedirect)


def safe_name(name):
    return (isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,199}", name)
            and not name.endswith(".") and not re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", name))


def identity(environment):
    token = environment.get("GH_TOKEN")
    api = environment.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    repository, run_id = environment.get("GITHUB_REPOSITORY", ""), environment.get("GITHUB_RUN_ID", "")
    parsed = urllib.parse.urlsplit(api)
    if (not token or parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)
            or not re.fullmatch(r"[1-9][0-9]*", run_id)):
        raise ArtifactError("Trusted GitHub run identity and GH_TOKEN are required")
    return api, repository, run_id, token


def api_request(url, token):
    return urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": USER_AGENT,
                                               "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"})


def list_artifacts(api, repository, run_id, token, name=None):
    selected, page = {}, 1
    while True:
        url = f"{api}/repos/{repository}/actions/runs/{run_id}/artifacts?per_page=100&page={page}"
        for attempt in range(ATTEMPTS):
            try:
                with API_OPENER.open(api_request(url, token), timeout=120) as response:
                    data = json.load(response)
                artifacts = data["artifacts"]
                if not isinstance(artifacts, list):
                    raise ValueError("Invalid artifact list")
                break
            except Exception:
                if attempt + 1 == ATTEMPTS:
                    raise ArtifactError("Could not list this GitHub run's artifacts") from None
                time.sleep(attempt + 1)
        for artifact in artifacts:
            if artifact.get("expired") is not False or (name is not None and artifact.get("name") != name):
                continue
            artifact_name, artifact_id = artifact.get("name"), artifact.get("id")
            if (not safe_name(artifact_name) or not isinstance(artifact_id, int) or isinstance(artifact_id, bool)
                    or artifact_id <= 0 or not isinstance(artifact.get("digest"), str)
                    or not re.fullmatch(r"sha256:[a-f0-9]{64}", artifact["digest"])
                    or str(artifact.get("workflow_run", {}).get("id", run_id)) != run_id):
                raise ArtifactError("Artifact metadata is invalid or has no mandatory SHA-256 digest")
            previous = selected.get(artifact_name)
            if previous is None or artifact_id > previous["id"]:
                selected[artifact_name] = artifact
        if len(artifacts) < 100:
            break
        page += 1
    if not selected:
        raise ArtifactError("No matching, non-expired artifacts exist for this GitHub run")
    return [selected[key] for key in sorted(selected)]


def blob_response(api, repository, artifact, token):
    url = f"{api}/repos/{repository}/actions/artifacts/{artifact['id']}/zip"
    try:
        return API_OPENER.open(api_request(url, token), timeout=120)
    except urllib.error.HTTPError as redirect:
        if redirect.code not in (301, 302, 303, 307, 308):
            redirect.close()
            raise
        location = redirect.headers.get("Location", "")
        redirect.close()
        parsed = urllib.parse.urlsplit(location)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise ArtifactError("Artifact service returned an unsafe download redirect") from None
        # A fresh unauthenticated request prevents credentials from crossing hosts.
        return urllib.request.urlopen(urllib.request.Request(location, headers={"User-Agent": USER_AGENT}), timeout=120)


def download_zip(api, repository, artifact, token, destination):
    checksum = hashlib.sha256()
    with blob_response(api, repository, artifact, token) as response, destination.open("xb") as stream:
        while block := response.read(1024 * 1024):
            stream.write(block)
            checksum.update(block)
    if f"sha256:{checksum.hexdigest()}" != artifact["digest"]:
        raise ArtifactError("Artifact ZIP SHA-256 mismatch")


def zip_members(bundle):
    members, names = [], {}
    for member in bundle.infolist():
        # ZipInfo normalizes backslashes on Windows and truncates NUL bytes;
        # validate the original stored name before relying on its parsed path.
        raw = member.orig_filename
        normalized = raw[:-1] if raw.endswith("/") else raw
        parts = normalized.split("/")
        if (not normalized or "\\" in raw or PurePosixPath(raw).is_absolute()
                or any(part in ("", ".", "..") or part.endswith((".", " "))
                       or re.search(r'[<>:"|?*\x00-\x1f]', part)
                       or re.fullmatch(r"(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?", part) for part in parts)):
            raise ArtifactError("Artifact ZIP contains an unsafe member path")
        key = normalized.casefold()
        if key in names:
            raise ArtifactError("Artifact ZIP contains duplicate member paths")
        mode = member.external_attr >> 16
        kind = stat.S_IFMT(mode)
        if kind not in (0, stat.S_IFREG, stat.S_IFDIR) or (kind == stat.S_IFDIR and not member.is_dir()):
            raise ArtifactError("Artifact ZIP contains a symlink or special file")
        names[key] = member.is_dir()
        members.append((member, parts))
    for key in names:
        parent = PurePosixPath(key).parent
        while parent != PurePosixPath("."):
            if parent.as_posix() in names and not names[parent.as_posix()]:
                raise ArtifactError("Artifact ZIP contains conflicting file/directory paths")
            parent = parent.parent
    return members


def extract_zip(archive, destination):
    with zipfile.ZipFile(archive) as bundle:
        members = zip_members(bundle)
        if bundle.testzip() is not None:
            raise ArtifactError("Artifact ZIP CRC verification failed")
        destination.mkdir()
        for member, parts in members:
            target = destination.joinpath(*parts)
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with bundle.open(member) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output, length=1024 * 1024)


def download(output, name=None, environment=None):
    environment = os.environ if environment is None else environment
    api, repository, run_id, token = identity(environment)
    if name is not None and not safe_name(name):
        raise ArtifactError("Invalid requested artifact name")
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise ArtifactError("Artifact output must not already exist")
    output.parent.mkdir(parents=True, exist_ok=True)
    artifacts = list_artifacts(api, repository, run_id, token, name)
    with tempfile.TemporaryDirectory(prefix=f".{output.name}-download-", dir=output.parent) as temporary:
        work = Path(temporary)
        staged = work / "verified"
        if name is None:
            staged.mkdir()
        for artifact in artifacts:
            archive = work / f"{artifact['id']}.zip"
            destination = staged if name is not None else staged / artifact["name"]
            for attempt in range(ATTEMPTS):
                try:
                    download_zip(api, repository, artifact, token, archive)
                    extract_zip(archive, destination)
                    archive.unlink()
                    break
                except Exception as error:
                    archive.unlink(missing_ok=True)
                    if destination.exists():
                        shutil.rmtree(destination)
                    if attempt + 1 == ATTEMPTS:
                        reason = str(error) if isinstance(error, ArtifactError) else "Network transfer or ZIP integrity check failed"
                        raise ArtifactError(f"Artifact {artifact['name']} failed after three attempts: {reason}") from None
                    time.sleep(attempt + 1)
            print(f"Verified artifact: {artifact['name']}", flush=True)
        if output.exists() or output.is_symlink():
            raise ArtifactError("Artifact output appeared before atomic installation")
        staged.rename(output)
    return artifacts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name")
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()
    try:
        download(arguments.output, arguments.name)
    except ArtifactError as error:
        parser.exit(1, f"Artifact download failed: {error}\n")
