# AlgorithVideo source and distribution readiness

The canonical source repository is [algorithco/algorith-video](https://github.com/algorithco/algorith-video), maintained by Algorithco. AlgorithVideo 0.1.0 has its own identity, supplied logo, developer metadata and isolated settings namespace. Release targets are Windows x64, macOS arm64/x64 and Linux x64.

## Public source repository

- The project uses the [MIT license](../LICENSE). Original BridgeMind copyright and permission notices remain in the root and engine licenses; [source attribution](ATTRIBUTION.md) records the upstream repository and starting commit.
- Fonts, YuNet, platform marks and dependencies retain their individual terms in [third-party notices](../THIRD_PARTY_NOTICES.md) and accompanying license files. Publishing the source does not relicense those assets.
- [Contributing](../CONTRIBUTING.md), the [code of conduct](../CODE_OF_CONDUCT.md), issue forms and the pull request template describe collaboration. Report vulnerabilities privately using [SECURITY.md](../SECURITY.md); maintainer contact is [otashdev1@gmail.com](mailto:otashdev1@gmail.com).
- [CI](../.github/workflows/ci.yml) defines TypeScript, lint, mocked JavaScript/bridge tests, production build and Python engine regression checks. A workflow definition or an earlier local result is not a claim that a particular new commit has passed GitHub Actions; inspect that commit's checks.
- Pre-publication history and working-diff secret scans found no real credentials. Review the final staged tree and run a fresh secret scan before each source push. Never commit provider keys, `.env`, private media, signing material, local profiles, dependency installations or generated build/runtime directories.

The normal Git repository is the source publication path. The older public-draft manifest/export script remains a development utility, not a prerequisite for publishing this repository.

## Packaged releases

Source publication and native package verification have separate acceptance criteria. Historical local results are recorded in [the rebranding verification report](ALGORITHVIDEO_REBRANDING_VERIFICATION.md) and [Windows build report](WINDOWS_0_1_0_RELEASE.md); those reports do not describe the result of a later GitHub release run.

The [release workflow](../.github/workflows/release.yml) builds native packages on GitHub Actions and waits for the complete platform matrix before publication. Review the exact run, bundled runtime, source/license materials and artifact checksums described in [RELEASING.md](RELEASING.md). The first release is unsigned, with ad-hoc signing on macOS and no notarization; its release notes must state that status.

A later signed distribution requires actual Algorithco publisher identities and notarization/signature acceptance. Keep automatic updates disabled until a signed upgrade between two application versions has been verified. Creating a GitHub release does not by itself enable automatic downloads.
