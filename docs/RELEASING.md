# Releasing AlgorithVideo

[Overview](../README.md) · [Source and distribution readiness](OPEN_SOURCE_READINESS.md) · [Third-party notices](../THIRD_PARTY_NOTICES.md)

Desktop packages are built and verified in [GitHub Actions](https://github.com/algorithco/algorith-video/actions/workflows/release.yml), then published to [GitHub Releases](https://github.com/algorithco/algorith-video/releases). The release process does not require building an installer on a maintainer's computer.

## Platforms and files

| Build target | Native runner | Published packages |
| --- | --- | --- |
| Windows x64 | Windows Server 2022 | `AlgorithVideo-<version>-win-x64.exe` |
| macOS Apple Silicon | macOS 15 arm64 | `AlgorithVideo-<version>-mac-arm64.dmg` and `.zip` |
| macOS Intel | macOS 15 Intel | `AlgorithVideo-<version>-mac-x64.dmg` and `.zip` |
| Linux x64 | Ubuntu 24.04 | `AlgorithVideo-<version>-linux-x64.AppImage` and `.deb` |

The current package version is `0.1.0`, corresponding to the release tag `v0.1.0`. Each desktop package includes the application, clipping engine, standalone Python, FFmpeg, ffprobe and the yt-dlp launcher. The build must stage native dependencies for the same architecture as its Electron package; a development virtual environment is not a relocatable release runtime.

Windows/Linux corresponding sources can exceed GitHub's per-asset limit. They are published as numbered `ffmpeg-sources-windows-linux.tar.gz.partNN` files with `SOURCE-RECONSTRUCTION.txt` and `ffmpeg-source-manifest.json`. Download every part, concatenate them in the recorded order, and verify the combined archive digest before extraction. Installers do not require these source files. The workflow caches the complete source bundle by its source pins and collection script; staging and publication still verify the cached bytes against the source manifest.

## Start a release in GitHub

1. Merge the intended source and dependency changes into `main`. Confirm its source CI checks have passed.
2. Check `package.json`, `CHANGELOG.md`, privacy documentation and bundled-license notices for the version being released. Do not reuse a published version for changed binaries.
3. Open **Actions → the desktop release workflow → Run workflow**, select the intended `main` revision and start the run. The workflow derives the release version from `package.json` and builds the complete platform matrix.
4. Inspect the run's native build and verification jobs. A failed target must be fixed and rebuilt before publishing the complete release.
5. The publication job collects the verified platform assets, creates the versioned GitHub release and uploads its packages, manifest and checksums. Confirm the published tag points to the source revision recorded in the manifest.

Maintainers can also start the workflow with GitHub CLI:

```bash
gh workflow run release.yml --repo algorithco/algorith-video --ref main
```

Packaging steps use `--publish never` so an individual operating-system job cannot create a partial release. Publication is a separate final job that waits for all required build jobs. Build jobs need read access to source; only publication needs permission to create release assets.

## What the runner must verify

The release workflow should retain evidence from the exact source revision and final package bytes:

- Hash verification for downloaded standalone Python/media archives and hash-locked Python dependency installation.
- Native architecture and relocatable Python/media paths, without depending on a developer's system tools.
- Bundled license texts, native runtime provenance and corresponding-source material for redistributed FFmpeg/dependencies.
- Application version/name, required Electron security fuses and the expected package formats.
- The packaged Python imports, face model, yt-dlp launcher, captions, H.264 output, speed changes and audio timing. `scripts/release/verify-runtime.py` copies resources into a path containing spaces before running its smoke checks.
- Packaged application startup with an isolated profile and no real provider keys. Installation checks should use a dedicated runner-temporary directory.
- Final release-asset names, lengths and digests. `release-manifest.json` records the source revision and assets; `SHA256SUMS.txt` lets downloaders verify the published bytes.

Paid AI processing and real social posts are not required for package verification. Use synthetic media and isolated profiles for acceptance checks. Source CI passing does not replace the native package checks, and an earlier local build report is not evidence for a later artifact.

## First-release signing status

The first desktop release has no configured publisher certificate. Windows packages are unsigned. macOS packages use ad-hoc signing and are not notarized. State this in release notes so users can distinguish these packages from a later publisher-signed release. Operating systems may display unverified-publisher or notarization warnings.

For a later signed Windows release, configure Algorithco's actual signing account and certificate subject. `scripts/release/windows-config.cjs` requires `SIGNING_PUBLISHER`, `SIGNING_ENDPOINT`, `SIGNING_ACCOUNT`, and `SIGNING_PROFILE`; `verify-windows.ps1` verifies timestamped signatures from that exact publisher. These signed-release checks must not be weakened or described as passed for an unsigned build.

For a later signed macOS release, configure the real Developer ID identity and notarization credentials, verify the signed application and final notarized packages, and refresh any digests affected by signing or stapling. Never copy an upstream project's signing identity.

## Automatic updates

Automatic updates remain disabled for the first release. Source hosting and a manual-download GitHub release are separate from an accepted signed update feed. Enable updates only after a signed upgrade between two AlgorithVideo versions has been tested on the target platform, with matching publisher identities and final-byte update metadata.

Keep package signature/checksum verification and the application's process/media trust boundaries enabled. Publication credentials and signing material belong in GitHub configuration, never in source files or release assets.
