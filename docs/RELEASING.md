# AlgorithVideo 0.1.0 Windows desktop packaging

AlgorithVideo starts as a new Algorithco application at **0.1.0**. The active distribution target is **Windows x64**, using an NSIS installer. Source is hosted at [algorithco/algorith-video](https://github.com/algorithco/algorith-video). A signed binary release and update feed have not been configured. `publish: null` and `--publish never` prevent implicit publishing; automatic updates stay off.

## Build the installer

The packaged application needs the compiled Electron UI, the clipping engine, a relocatable Python distribution in `engine-venv/` and media executables in `engine-bin/`. A development virtual environment is not a relocatable release runtime.

1. Install Node dependencies with `npm ci`.
2. Run `python scripts/release/stage-python-runtime.py` to stage or safely reuse the verified standalone Windows Python distribution and hash-locked engine dependencies. Stage the pinned Windows FFmpeg/ffprobe bundle and native yt-dlp launcher in `engine-bin/`, with licenses and provenance.
3. Run `npm run dist` (or its `dist:win` / `dist:win-x64` aliases).
4. The output is `dist/AlgorithVideo-0.1.0-win-x64.exe`; `dist/win-unpacked/` holds the unpacked application for runtime inspection.

The default command builds only Windows x64 and passes `--publish never`. No macOS or Linux package commands or active targets are configured.

## Verify the Windows package

Check application and installer version metadata, the AlgorithVideo name/icon, packaged Python imports, face detector assets, FFmpeg captions, yt-dlp and a real local render from a path containing spaces. The runtime verifier is `python scripts/release/verify-runtime.py dist/win-unpacked/resources`.

Check installation into a new dedicated folder, startup, Library paths and uninstall. Keep test profiles separate from existing user data. Paid clipping and social posting require the user's provider accounts and are not needed for an offline package check.

The local installer is unsigned. Before an official signed release, configure Algorithco's actual signing account and certificate subject. The Windows signing helpers require `SIGNING_PUBLISHER`, `SIGNING_ENDPOINT`, `SIGNING_ACCOUNT` and `SIGNING_PROFILE`. Existing signature/checksum validation must remain enabled.

## Future updates

Enable updates only after the matching Windows signing identity, reviewed GitHub release artifacts and update metadata are configured and a signed upgrade between two AlgorithVideo versions has been tested. Creating the source repository alone does not enable updates. This local 0.1.0 installer does not depend on an update server.
