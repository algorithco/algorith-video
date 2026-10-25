> Historical rebranding record: the temporary 0.2.0 working version was superseded by the fresh AlgorithVideo 0.1.0 Windows x64 release. The test results and unconfigured public links below belong to that earlier stage. See [README](../README.md) for the public source repository and [Windows packaging](RELEASING.md) for the current build.

# AlgorithVideo local rebranding verification

Date: 2026-10-24. Product: AlgorithVideo 0.2.0. Developer: Algorithco.
Workspace: `D:/repos/algorithco/algorithco-clip`. Branch: `codex/algorithvideo-rebrand`.

## Delivered

- Product and company identity across renderer, native window/menu/About, assistant prompts and tools, Python configuration, package metadata and installer configuration.
- New preload API `window.algorithvideo`, appId `com.algorithco.algorithvideo`, `ALGORITHVIDEO_*` environment names and AlgorithVideo storage/output namespace.
- The exact user-supplied logo, preserved byte for byte, plus PNG/ICO/ICNS exports, compact SVG mark, outlined wordmarks and local social SVG assets.
- Black/white/yellow theme with dark foregrounds on yellow primary controls.
- No invented public endpoints: site, repository and release links remain empty; related buttons are hidden. No release feed or signing identity is configured; local builds never download updates.
- Compatibility reads for previous library bookmarks and manual posted markers, with regression coverage for clearing them and writing new markers.
- Local development guides, notices, changelog, source export inventory and repeatable icon tooling.
- Settings section navigation keeps the application shell fixed and respects reduced motion.
- Windows test infrastructure fixes for CLI path construction, native Node invocation of the build CLI, CPU H.264 fixture selection and closing isolated apps before removing their fixtures.

## Validation

| Check | Final result |
| --- | --- |
| `npm run typecheck` | Passed |
| `npm run lint` | Passed |
| `npm test` | Passed: 505 passed, 2 platform-specific skips across desktop, renderer, Zernio, bridge and release checks |
| `npm run test:renderer` after Settings navigation fix | 47 passed |
| `npm run build` | Passed; output in `out/` |
| `npm run icons` and brand artifact checks | Passed; original logo SHA256 matches the supplied file |
| Full engine suite, `pytest -q --timeout=180 engine/tests` | 1062 passed, 11 skipped |
| Targeted longform/encoder suite | 34 passed, including a real captioned video render |
| Branding and local-file E2E | 2 passed: new identity/API/About and local media ranges, playback and seeking |
| `git diff --check` | Passed |

The initial engine run exposed an inherited test assumption that every non-x264 build provided macOS VideoToolbox. The fixture now selects an available CPU OpenH264 encoder on Windows, and the complete engine suite passes. The native media E2E teardown was corrected to close the isolated Electron app before deleting its temporary profile.

## Screenshots

- [Create](assets/algorithvideo-create.png)
- [About](assets/algorithvideo-about.png)

Screenshots come from the actual built app with an isolated temporary profile and no provider keys. The temporary storage path visible in About is the test profile, not the product's default export directory.

## Local environment and boundaries

Windows x64, Node.js 24.13.0, Python 3.12.10. The Python runtime dependencies were installed from the hash-locked requirements into `engine/.venv`. The unavailable original FFmpeg archive was replaced for local development only with the official LGPL shared 8.1 asset verified against SHA256 `edc7450333aae4042e1f4670aa7bcafe4265324ba9f75abf8de49e8b52812389`; the production runtime lockfile is preserved.

Live paid provider clipping, real social posts, signed installers, public hosting, repository creation and native macOS/Linux installation were not part of this local implementation. Making real AI clips requires the user's OpenRouter key and credit. Original MIT and third-party notices remain in the source. Old product strings exist only for attribution, the earlier audit plan and explicit compatibility/negative test fixtures, not as active product identity.

## Start

```powershell
cd D:/repos/algorithco/algorithco-clip
npm run dev
```

Use Settings → System check, then connect your OpenRouter key. See [local development](LOCAL_DEVELOPMENT.md) for reproducible setup.
