#!/usr/bin/env python3
"""Stage a verified, relocatable Windows Python runtime without a system venv.

Safe to rerun: an existing engine-venv is reused only when its archive and
requirements provenance match, then its imports are verified again.
"""
import argparse
import hashlib
import json
import os
import platform
import runpy
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
LICENSE_SHA256 = "3b2f81fe21d181c499c59a256c8e1968455d6689d269aa85373bfb6af41da3bf"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def remove_console_wrappers(runtime):
    # pip-generated Windows console EXEs embed the staging interpreter path.
    # The desktop invokes modules via the root python.exe and the separately
    # compiled engine-bin/yt-dlp.exe, so these unused wrappers must not ship.
    scripts = runtime / "Scripts"
    for launcher in scripts.glob("*.exe"):
        if launcher.parent.resolve() != scripts.resolve() or launcher.is_symlink():
            raise RuntimeError("Unsafe Python console launcher")
        launcher.unlink()


def verify(runtime):
    interpreter = runtime / "python.exe"
    if not interpreter.is_file() or not (runtime / "PYTHON-LICENSE").is_file():
        raise RuntimeError("The standalone Python runtime is incomplete")
    environment = dict(os.environ)
    for name in ["PYTHONHOME", "PYTHONPATH", "VIRTUAL_ENV"]:
        environment.pop(name, None)
    environment.update(PYTHONPATH=str(ROOT / "engine"), PYTHONDONTWRITEBYTECODE="1", PYTHONNOUSERSITE="1")
    with tempfile.TemporaryDirectory(prefix="AlgorithVideo Python acceptance ") as temporary:
        probe = subprocess.run(
            [str(interpreter), "-P", "-c", "import json,sys,cv2,yt_dlp; from pathlib import Path; from clip_engine.bridge_contract import BRIDGE_CONTRACT_VERSION; from clip_engine.services.ai_clipping_pipeline import ClippingJobRequest; from clip_engine.services.layout_analyzer import LayoutAnalyzer; assert LayoutAnalyzer().available, 'Missing bundled face detector'; print(json.dumps({'python':sys.version.split()[0], 'prefix':sys.prefix, 'base_prefix':sys.base_prefix, 'opencv':cv2.__version__, 'contract':BRIDGE_CONTRACT_VERSION}))"],
            cwd=temporary, env=environment, capture_output=True, text=True, check=True, timeout=60,
        )
    result = json.loads(probe.stdout.strip())
    if Path(result["prefix"]).resolve() != runtime.resolve() or Path(result["base_prefix"]).resolve() != runtime.resolve():
        raise RuntimeError("Python runtime depends on another installation")
    print(json.dumps(result), flush=True)


def stage(verify_only=False):
    if sys.platform != "win32" or platform.machine().lower() not in {"amd64", "x86_64"}:
        raise RuntimeError("Use a native Windows x64 host")
    runtime = ROOT / "engine-venv"
    lock = json.loads((ROOT / "scripts/release/runtime-lock.json").read_text())
    py = lock["python"]
    target = py["windows"]
    filename = f'cpython-{py["version"]}+{py["tag"]}-{target["target"]}-install_only_stripped.tar.gz'
    source = f'https://github.com/astral-sh/python-build-standalone/releases/download/{py["tag"]}/{quote(filename, safe="")}'
    requirements = ROOT / "engine/requirements.lock"
    expected = {"version": py["version"], "target": target["target"], "source": source, "sha256": target["sha256"], "requirements_sha256": digest(requirements), "license_sha256": LICENSE_SHA256}
    marker = runtime / "PYTHON-PROVENANCE.json"
    if runtime.exists():
        if runtime.is_symlink() or not marker.is_file() or json.loads(marker.read_text()) != expected:
            raise RuntimeError("Existing engine-venv does not match the verified lock; preserve it and stage from a clean target")
        if digest(runtime / "PYTHON-LICENSE") != LICENSE_SHA256:
            raise RuntimeError("Existing Python license does not match the pinned notice")
        if not verify_only:
            remove_console_wrappers(runtime)
        verify(runtime)
        return
    if verify_only:
        raise RuntimeError("Standalone Python runtime has not been staged")
    helpers = runpy.run_path(str(ROOT / "scripts/release/stage-runtime.py"), run_name="algorithvideo_runtime_helpers")
    with tempfile.TemporaryDirectory(prefix="algorithvideo-standalone-python-") as temporary:
        work = Path(temporary).resolve()
        archive = work / filename
        print(f"Downloading verified Python {py['version']} Windows x64", flush=True)
        helpers["download"](source, archive, target["sha256"])
        helpers["extract"](archive, work / "extracted")
        staged = work / "extracted/python"
        interpreter = staged / "python.exe"
        if not interpreter.is_file():
            raise RuntimeError("Unexpected standalone Python archive layout")
        subprocess.run([str(interpreter), "-m", "pip", "install", "--no-compile", "--require-hashes", "-r", str(requirements)], check=True)
        helpers["download"](f'https://raw.githubusercontent.com/python/cpython/v{py["version"]}/LICENSE', staged / "PYTHON-LICENSE", LICENSE_SHA256)
        (staged / "PYTHON-PROVENANCE.json").write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8", newline="\n")
        remove_console_wrappers(staged)
        # Both absolute paths are verified before moving a directory. This is a
        # new target; no pre-existing runtime or user directory is deleted.
        if not staged.resolve().is_relative_to(work) or runtime.parent.resolve() != ROOT.resolve() or runtime.exists():
            raise RuntimeError("Unsafe or occupied standalone runtime target")
        shutil.move(str(staged), str(runtime))
    verify(runtime)
    print("Verified standalone Windows Python runtime staged in engine-venv", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    stage(parser.parse_args().verify_only)
