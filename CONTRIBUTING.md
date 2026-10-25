# Contributing to AlgorithVideo

AlgorithVideo is maintained by [Algorithco](https://github.com/algorithco). Contributions to the application, tests, documentation, accessibility, and translations are welcome. By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Before you start

- Search the [existing issues](https://github.com/algorithco/algorith-video/issues) before reporting a bug or proposing a feature.
- For bugs, include the application version, Windows version, installation method, and steps that work with a public or synthetic video. Describe what you expected and what happened.
- For substantial changes, open a feature request explaining the problem and proposed behavior before starting implementation. A discussion helps avoid duplicated work and changes that do not fit the project.
- Report suspected vulnerabilities privately using [SECURITY.md](SECURITY.md). Do not publish an exploit, real credentials, private video, or unredacted logs in an issue or pull request.

## Set up a development checkout

The supported installer target is Windows x64. Development requires Node.js 22 or a newer version supported by the dependencies, Python 3.12, and FFmpeg/ffprobe with the libass-backed `ass` caption filter.

Fork the repository, then run the following in PowerShell, replacing `YOUR-USERNAME` with your GitHub username:

```powershell
git clone https://github.com/YOUR-USERNAME/algorith-video.git
cd algorith-video
git remote add upstream https://github.com/algorithco/algorith-video.git
git switch -c codex/describe-your-change
npm ci
python -m venv engine/.venv
engine/.venv/Scripts/python.exe -m pip install --require-hashes -r engine/requirements.lock
npm run dev
```

Development detects the Python environment in `engine/.venv` and media tools in `engine-bin/`; otherwise it checks `PATH`. Check **Settings → System check** after launching. See the [development guide](docs/development.md) for the project layout and [Windows packaging](docs/RELEASING.md) for creating an installer.

The mocked test suites use isolated app profiles and do not need real provider credentials. Creating real clips uses your own OpenRouter account and credit; publishing uses your own Zernio account. Review [AI and privacy](docs/ai-and-privacy.md) before using private media. Enter credentials in the app rather than source files or test fixtures.

## Make a focused change

- Keep the React interface, isolated preload API, Electron main process, and Python engine responsibilities separate. See [Architecture](docs/ARCHITECTURE.md).
- Validate data at IPC, saved-file, provider-response, and subprocess boundaries. Keep provider keys out of renderer state, tool results, and logs.
- Match the surrounding code style and reuse existing components and contracts. Avoid unrelated formatting or dependency upgrades in a behavior change.
- Add a focused regression test when fixing a bug or changing a meaningful boundary. Documentation-only and visual-copy changes usually do not need new tests.
- Update the relevant guides and [CHANGELOG.md](CHANGELOG.md) when behavior changes. Include before/after screenshots for interface changes, using public or synthetic content.
- Preserve source attribution, copyright notices, and third-party licenses. Check [attribution](docs/ATTRIBUTION.md) and [third-party notices](THIRD_PARTY_NOTICES.md) when adding or replacing code, fonts, models, or media tools. Do not reuse upstream maintainers' contact details or signing identities for this edition.

## Validate your change

For application code, run:

```powershell
npm run typecheck
npm run lint
npm test
npm run build
```

For engine changes, install the locked test tools and run the engine tests as well:

```powershell
engine/.venv/Scripts/python.exe -m pip install --require-hashes -r scripts/python-tools/pytest.lock
engine/.venv/Scripts/python.exe -m pytest -q engine/tests
```

Media tests need FFmpeg and ffprobe on `PATH`. End-to-end interface tests are available through `npm run test:e2e`; run them for changes to the affected desktop flow. Installer or bundled-runtime changes also need the acceptance checks in [Windows packaging](docs/RELEASING.md).

Document failures, skipped checks, and environment limitations in the pull request. Do not describe a check as passed if it did not finish. For documentation-only changes, check links, commands, and Markdown rendering instead of running unrelated application tests.

## Open a pull request

Push your branch to your fork and open a pull request against the repository's default branch. Use a clear title and explain the problem, resulting behavior, and validation. Link the relevant issue when there is one. Small, reviewable pull requests are easier to assess than a collection of unrelated changes.

Do not commit generated installers, `out/`, `dist/`, `node_modules/`, Python virtual environments, local clip libraries, credentials, or private recordings. Keep `package-lock.json` and the Python lockfiles consistent with intentional dependency changes.

Respond to review feedback in the same pull request. Maintainers may request changes or decline a proposal based on correctness, maintenance cost, privacy, accessibility, or project scope. Review timing depends on maintainer availability.
