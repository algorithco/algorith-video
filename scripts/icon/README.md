# AlgorithVideo brand assets

The white geometric frame and yellow play mark were supplied by Algorithco. The original file is `resources/algorithvideo-logo-source.png`: 1254 × 1254 RGB PNG with a black background, SHA256 `a9743c645fb6fd27619c29897305c56647a55ba19da92784dc0e9b4a4d59616a`.

`npm run icons` exports the same artwork into `build/icon.png`, a multi-size Windows `build/icon.ico`, macOS `build/icon.icns`, full/compact raster-backed SVG icons, a compact SVG mark and dark/light SVG wordmarks. The wordmarks use outlined Geist glyphs so a system font installation is unnecessary. The source PNG is not redrawn. Viewport framing in the SVG mark improves legibility in the collapsed sidebar.

The exporter is `scripts/icon/export-assets.py` and runs on Windows, macOS and Linux. Set up `scripts/icon/.venv` with [requirements.txt](requirements.txt), then run `npm run icons`; see [local development](../../docs/LOCAL_DEVELOPMENT.md). `PYTHON` can select another interpreter with those dependencies. `build-icons.sh` and `build-logo.py` remain compatibility entry points.

Open `scripts/icon/icon.html` to inspect 16–128px icons on dark and light surfaces. Keep the source as supplied and regenerate exports together after an approved source replacement.
