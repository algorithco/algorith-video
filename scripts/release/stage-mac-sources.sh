#!/usr/bin/env bash
set -euo pipefail

# Collect corresponding sources after prepare-resources.sh. This never compiles
# a formula; brew fetch verifies its source/resource/patch checksums. The full
# output is a GitHub release asset, separate from the runnable app bundle.
[[ "${GITHUB_ACTIONS:-}" == "true" ]] || { echo "Run source collection only in GitHub Actions." >&2; exit 1; }
[[ "$(uname -s)" == "Darwin" ]] || { echo "Use a native macOS runner." >&2; exit 1; }
arch="${1:?Pass arm64 or x64}"
case "$arch:$(uname -m)" in
  arm64:arm64|x64:x86_64) ;;
  *) echo "Source archive architecture must match the runner." >&2; exit 1 ;;
esac
cd "$(dirname "$0")/../.."
export HOMEBREW_NO_AUTO_UPDATE=1
export HOMEBREW_NO_ANALYTICS=1
python3 - "$arch" <<'PY'
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

root = Path.cwd().resolve()
arch = sys.argv[1]
media = root / 'engine-bin'
inventory = media / 'BUNDLED_LIBRARIES.txt'
required = ['FFMPEG-SOURCE.tar.xz', 'FFMPEG-LICENSE', 'FFMPEG-SOURCE.txt', 'BUNDLED_LIBRARIES.txt']
for name in required:
    if not (media / name).is_file() or (media / name).is_symlink():
        raise RuntimeError(f'Missing regular packaged source/notice file: {name}')
if not (media / 'THIRD_PARTY_LICENSES').is_dir():
    raise RuntimeError('Run native resource preparation before collecting sources')

formulae = {}
for line in inventory.read_text(encoding='utf-8').splitlines():
    if not line.strip():
        continue
    fields = line.split()
    if len(fields) != 2 or not re.fullmatch(r'[a-z0-9][a-z0-9@+._-]*', fields[0]):
        raise RuntimeError('Malformed bundled-library inventory')
    formula, version = fields
    if formula in formulae or not re.fullmatch(r'[A-Za-z0-9+._-]+', version):
        raise RuntimeError('Duplicate formula or invalid bundled version')
    formulae[formula] = version
if 'libass' not in formulae:
    raise RuntimeError('The inventory must include the shipped libass library')

output = root / 'release-sources'
output.mkdir(exist_ok=True)
if output.is_symlink():
    raise RuntimeError('Source output directory cannot be a symlink')
archive = output / f'ffmpeg-sources-mac-{arch}.tar.gz'
if archive.exists():
    raise RuntimeError('Source archive already exists; use a clean release checkout')

def run(*args, env=None):
    return subprocess.check_output(args, env=env, text=True).strip()

def copy_regular(source, destination):
    if source.is_symlink() or not source.is_file():
        raise RuntimeError(f'Expected a regular source file: {source.name}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)

source_sha = run('git', 'rev-parse', 'HEAD')
if not re.fullmatch(r'[0-9a-f]{40}', source_sha):
    raise RuntimeError('Invalid source revision')

with tempfile.TemporaryDirectory(prefix='algorithvideo-mac-sources-') as temporary:
    work = Path(temporary).resolve()
    payload = work / f'ffmpeg-sources-mac-{arch}'
    payload.mkdir()
    for name in required:
        copy_regular(media / name, payload / name)
    for notice in (media / 'THIRD_PARTY_LICENSES').rglob('*'):
        if notice.is_symlink():
            raise RuntimeError('Bundled license inventory contains a symlink')
        if notice.is_file():
            copy_regular(notice, payload / 'THIRD_PARTY_LICENSES' / notice.relative_to(media / 'THIRD_PARTY_LICENSES'))
    for script in ['prepare-resources.sh', 'build-ffmpeg-mac.sh', 'stage-ffmpeg-libs-mac.sh']:
        copy_regular(root / 'scripts' / script, payload / 'build-scripts' / script)

    records = []
    cellar = Path(run('brew', '--cellar')).resolve()
    for formula, version in sorted(formulae.items()):
        # A new isolated cache for every formula avoids collecting a developer
        # cache, other formulae's bottles, or unrelated runner downloads.
        cache = work / 'source-caches' / formula
        cache.mkdir(parents=True)
        env = dict(os.environ, HOMEBREW_CACHE=str(cache), HOMEBREW_NO_AUTO_UPDATE='1', HOMEBREW_NO_ANALYTICS='1')
        info_text = run('brew', 'info', '--json=v2', '--formula', formula, env=env)
        values = json.loads(info_text).get('formulae', [])
        if len(values) != 1 or values[0].get('name') != formula:
            raise RuntimeError(f'Unexpected Homebrew formula identity: {formula}')
        info = values[0]
        stable = info.get('versions', {}).get('stable')
        revision = info.get('revision', 0)
        stable_version = f'{stable}_{revision}' if revision else stable
        installed = {item.get('version') for item in info.get('installed', [])}
        if version != stable_version or version not in installed:
            raise RuntimeError(f'{formula}: bundled {version} does not match installed/current stable {stable_version}; refresh Homebrew before preparing the runtime')
        keg = cellar / formula / version
        if not keg.is_dir() or not keg.resolve().is_relative_to(cellar):
            raise RuntimeError(f'Installed keg is unavailable: {formula} {version}')

        target = payload / 'homebrew' / formula
        target.mkdir(parents=True)
        (target / 'formula-info.json').write_text(info_text + '\n', encoding='utf-8')
        recipe = run('brew', 'cat', '--formula', formula, env=env)
        if not recipe:
            raise RuntimeError(f'Missing source build recipe: {formula}')
        (target / f'{formula}.rb').write_text(recipe + '\n', encoding='utf-8')
        installed_recipe = keg / '.brew' / f'{formula}.rb'
        if installed_recipe.is_file():
            copy_regular(installed_recipe, target / 'installed-formula.rb')
        receipt = keg / 'INSTALL_RECEIPT.json'
        if receipt.is_file():
            copy_regular(receipt, target / 'INSTALL_RECEIPT.json')

        # Includes formula resources and external patches; inline DATA patches
        # remain in the formula recipe captured above.
        subprocess.run(['brew', 'fetch', '--formula', '--build-from-source', '--retry', formula], env=env, check=True)
        main_source = Path(run('brew', '--cache', '--formula', '--build-from-source', formula, env=env))
        if not main_source.exists() or not main_source.resolve().is_relative_to(cache):
            raise RuntimeError(f'Missing source payload in isolated cache: {formula}')
        downloads = cache / 'downloads'
        if not downloads.is_dir():
            raise RuntimeError(f'Missing fetched source/resource cache: {formula}')
        copied = 0
        for item in sorted(downloads.rglob('*')):
            if not item.resolve().is_relative_to(cache):
                raise RuntimeError(f'Source cache points outside its isolated directory: {formula}')
            if item.is_symlink():
                # Homebrew uses convenience symlinks; actual cached bytes are
                # copied by their regular-file paths without external links.
                continue
            if item.is_file():
                if '.bottle.' in item.name or item.name.endswith('.incomplete'):
                    raise RuntimeError(f'Unexpected bottle or incomplete source payload: {formula}')
                copy_regular(item, target / 'source-cache' / 'downloads' / item.relative_to(downloads))
                copied += 1
        if not copied:
            raise RuntimeError(f'No source/resource bytes were collected: {formula}')
        records.append({'formula': formula, 'version': version, 'stable_version': stable_version, 'source_files': copied})

    (payload / 'README.md').write_text(
        '# Corresponding macOS media sources\n\n'
        'These sources accompany the FFmpeg and Homebrew caption-library binaries in the matching AlgorithVideo release.\n'
        'FFMPEG-SOURCE.tar.xz contains the verified FFmpeg source. build-scripts/ records the configure, dependency-copy and loader-path changes.\n'
        'homebrew/ contains the exact recorded formula versions, recipes, installation receipts, fetched source archives, resources and patches.\n'
        'To rebuild a library, use its formula recipe and recorded Homebrew toolchain/dependencies; source-cache/downloads preserves the fetched bytes.\n'
        'The application dynamically links the bundled caption libraries; each component retains its own license in THIRD_PARTY_LICENSES/.\n',
        encoding='utf-8')
    files = []
    for item in sorted(payload.rglob('*')):
        if item.is_file():
            with item.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            files.append({'path': item.relative_to(payload).as_posix(), 'size': item.stat().st_size, 'sha256': digest})
    (payload / 'source-manifest.json').write_text(json.dumps({'product': 'AlgorithVideo', 'platform': f'mac-{arch}', 'source_sha': source_sha, 'formulae': records, 'files': files}, indent=2) + '\n', encoding='utf-8')
    with tarfile.open(archive, 'x:gz') as bundle:
        bundle.add(payload, arcname=payload.name, recursive=True)
print(f'Collected corresponding media sources: {archive}')
PY
