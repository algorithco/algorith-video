# AlgorithVideo changelog

The first Algorithco desktop application starts at version 0.1.0. Windows, macOS and Linux packages are built in GitHub Actions and published through GitHub Releases. Automatic updates remain disabled.

## [Unreleased]

### Added

- Public source repository at `algorithco/algorith-video` with contribution, conduct and private security-reporting policies.
- GitHub Actions source validation, dependency update configuration and issue/PR templates.
- A native GitHub Actions desktop release matrix for Windows x64, macOS arm64/x64 and Linux x64, with packaged runtime checks and final-asset checksums.

### Changed

- Documentation now includes a fresh-checkout quick start, provider data-flow summary and navigation index.
- Application project links point to the public repository; signed binary updates remain disabled.

## [0.1.0] - 2026-10-25

### Added

- First AlgorithVideo desktop release, developed by Algorithco, with Windows x64, macOS arm64/x64 and Linux x64 package targets.
- The supplied white-and-yellow logo, black/white/yellow interface and Windows installer icon.
- Local video clipping, caption editing and Library management with the bundled Python and media runtime.
- Assistant tools and optional publishing integrations using the user's own provider accounts.

### Changed

- Product, internal API, assistant tools, storage keys and installer metadata use the AlgorithVideo identity.
- Settings → About identifies Algorithco and shows version 0.1.0.
- Release installers are built on GitHub runners. First-release packages are unsigned, with ad-hoc signing on macOS and no notarization; automatic updates remain disabled.

[Unreleased]: #unreleased
[0.1.0]: #010---2026-10-25
