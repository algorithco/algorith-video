# Develop AlgorithVideo for Windows

[Overview](../README.md) · [Contributing](../CONTRIBUTING.md) · [Architecture](ARCHITECTURE.md)

AlgorithVideo **0.1.0** is the first Algorithco Windows x64 desktop release. Active installer targets and distribution commands are Windows-only.

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
| `npm run dist` | Build the Windows x64 NSIS installer without publishing |
| `npm run icons` | Export the supplied logo; only the Windows ICO is used for distribution |

## Packaging

Use a relocatable Python/media runtime rather than copying the development venv. Follow [Windows packaging](RELEASING.md), then verify the unpacked runtime and installed application.

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
