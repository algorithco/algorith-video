# Develop AlgorithVideo

[Overview](../README.md) · [Contributing](../CONTRIBUTING.md) · [Architecture](ARCHITECTURE.md)

AlgorithVideo **0.1.0** has release targets for Windows x64, macOS arm64/x64 and Linux x64. Desktop packages are built by native GitHub Actions runners; local development uses the source application.

## Set up

Development needs Node.js 22 or a newer dependency-compatible version, Python 3.12, and FFmpeg/ffprobe with the libass-backed `ass` caption filter. Provider keys are needed for real AI jobs, not the mocked test suites.

Open PowerShell in the source checkout:

```powershell
npm ci
python -m venv engine/.venv
engine/.venv/Scripts/python.exe -m pip install --require-hashes -r engine/requirements.lock
npm run dev
```

The app detects the in-repo Windows Python environment and media tools in `engine-bin/`. Settings → System check shows Python, yt-dlp, FFmpeg and the engine. See [local development](LOCAL_DEVELOPMENT.md) for this checkout's setup and original logo exports.

On macOS or Linux, use the corresponding environment executables:

```bash
npm ci
python3.12 -m venv engine/.venv
engine/.venv/bin/python3 -m pip install --require-hashes -r engine/requirements.lock
npm run dev
```

Install FFmpeg/ffprobe with the `ass` filter through your platform's package manager for development. The release workflow stages its own verified runtime instead of shipping the developer's virtual environment.

## Checks and scripts

Run `npm run typecheck`, `npm run lint`, `npm test` and `npm run build` before code changes are delivered. For engine changes install the tools from `scripts/python-tools/pytest.lock` in the development venv, then run `engine/.venv/Scripts/python.exe -m pytest -q engine/tests`. Media tests require FFmpeg/ffprobe on PATH. Windows symlink-dependent assertions skip when the OS denies link creation.

| Script | Purpose |
| --- | --- |
| `npm run dev` | Run the desktop app with hot reload |
| `npm run typecheck` | Check main/preload and renderer TypeScript |
| `npm run lint` | Check TypeScript and JavaScript source |
| `npm run build` | Compile the application into `out/` |
| `npm run test:main` | Desktop and process-boundary regressions |
| `npm run test:renderer` | Renderer state and parsing regressions |
| `npm run test:zernio` | Mocked social integration regressions |
| `npm run test:bridge` | Python bridge regressions |
| `npm run test:release` | Packaging metadata, integrity and release-helper checks |
| `npm run dist` | Packaging helper; official release builds run in GitHub Actions |
| `npm run icons` | Export the supplied logo and platform icon assets |

## Packaging

Use the [desktop release workflow](RELEASING.md) to build and publish installers in GitHub Actions. It uses native runners and relocatable Python/media runtimes instead of copying a development venv. Source CI and native package verification cover different boundaries; inspect both results before publishing.

## Project layout

```text
src/main/        Electron authority: settings, pipeline, IPC and integrations
src/preload/     Typed window.algorithvideo API
src/renderer/    React desktop interface
src/shared/      Shared product identity and contracts
bridge/          Python worker protocol and network guard
engine/          Video engine, assets and locked Python dependencies
scripts/icon/    Supplied-logo export tooling
```

See [DESIGN.md](../DESIGN.md) for the visual system and [Architecture](ARCHITECTURE.md) for trust boundaries.
