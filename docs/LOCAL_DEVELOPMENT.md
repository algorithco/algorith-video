# AlgorithVideo local development

The source repository is [algorithco/algorith-video](https://github.com/algorithco/algorith-video). The product is **AlgorithVideo 0.1.0 for Windows x64**, maintained by **Algorithco**. Binary update hosting and a publisher signing identity are not configured.

## Start

After completing the fresh-checkout setup in [README](../README.md), run `npm run dev` from the project folder. Development detects `engine/.venv/Scripts/python.exe`, `engine/.venv/Scripts/yt-dlp.exe` and media tools in `engine-bin/` automatically.

Use **Settings → System check** to verify tools, then add your own OpenRouter key. Making real clips requires provider credit. Rendering runs locally.

For a fresh Windows setup, use the commands in [README](../README.md). Windows x64 is the distribution target for this release.

## Local media tools

`engine-bin/` is ignored by Git. Media archives must be verified against their recorded SHA256. `engine-bin/RUNTIME-PROVENANCE.json` records the staged FFmpeg source. An installable release additionally requires a relocatable Python distribution in `engine-venv/`, the yt-dlp launcher and bundled notices; follow [Windows packaging](RELEASING.md).

For command-line media tests on this Windows checkout:

```powershell
$env:PATH = "$PWD/engine-bin;$PWD/engine/.venv/Scripts;$env:PATH"
npm test
```

## Export the supplied logo

The original supplied logo is preserved byte for byte at `resources/algorithvideo-logo-source.png`. To prepare the export environment once:

```powershell
python -m venv scripts/icon/.venv
scripts/icon/.venv/Scripts/python.exe -m pip install -r scripts/icon/requirements.txt
npm run icons
```

The exporter uses the original artwork for PNG/ICO/ICNS and frames it inside SVG for the compact mark. The Geist wordmark is converted to paths. No new generated logo is substituted.

## Existing clip libraries

A new profile writes settings under the AlgorithVideo application data directory and exports to `~/AlgorithVideo`. To use an existing library, select its folder in Settings. Original media stays in place. Earlier bookmark/posted markers are read through a compatibility layer. Re-enter provider keys through Settings; encrypted keys are not silently copied from another app identity.

## Build

`npm run build` creates `out/`. `npm run preview` runs that build locally. `npm run dist` creates the Windows x64 NSIS installer after runtime staging. Installer and verification details are in [RELEASING](RELEASING.md).
