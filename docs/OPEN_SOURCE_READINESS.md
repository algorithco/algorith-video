# AlgorithVideo source and distribution readiness

The canonical source repository is [algorithco/algorith-video](https://github.com/algorithco/algorith-video), maintained by Algorithco. The Windows x64 0.1.0 edition has its own AlgorithVideo identity, supplied logo, developer metadata and isolated settings namespace.

## Public source repository

- The project uses the [MIT license](../LICENSE). Original BridgeMind copyright and permission notices remain in the root and engine licenses; [source attribution](ATTRIBUTION.md) records the upstream repository and starting commit.
- Fonts, YuNet, platform marks and dependencies retain their individual terms in [third-party notices](../THIRD_PARTY_NOTICES.md) and accompanying license files. Publishing the source does not relicense those assets.
- [Contributing](../CONTRIBUTING.md), the [code of conduct](../CODE_OF_CONDUCT.md), issue forms and the pull request template describe collaboration. Report vulnerabilities privately using [SECURITY.md](../SECURITY.md); maintainer contact is [otashdev1@gmail.com](mailto:otashdev1@gmail.com).
- [CI](../.github/workflows/ci.yml) defines TypeScript, lint, mocked JavaScript/bridge tests, production build and Python engine regression checks. A workflow definition or an earlier local result is not a claim that a particular new commit has passed GitHub Actions; inspect that commit's checks.
- Pre-publication history and working-diff secret scans found no real credentials. Review the final staged tree and run a fresh secret scan before each source push. Never commit provider keys, `.env`, private media, signing material, local profiles, dependency installations or generated build/runtime directories.

The normal Git repository is the source publication path. The older public-draft manifest/export script remains a development utility, not a prerequisite for publishing this repository.

## Packaged releases

Source publication and a signed binary release have separate acceptance criteria. Local validation and historical results are recorded in [the rebranding verification report](ALGORITHVIDEO_REBRANDING_VERIFICATION.md) and [Windows release notes](WINDOWS_0_1_0_RELEASE.md); they do not imply a signed installer or tested updates on every operating system.

Before uploading an installer, follow [RELEASING.md](RELEASING.md): review the actual bundled native runtime and corresponding source/license materials, configure the appropriate Algorithco signing identity, verify installation and removal on Windows, and test any update feed before enabling automatic updates. A public source repository alone does not configure signing, publish an installer or enable automatic downloads.
