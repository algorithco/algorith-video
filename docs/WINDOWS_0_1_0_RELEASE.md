# AlgorithVideo 0.1.0 Windows build

AlgorithVideo by Algorithco starts at version 0.1.0 and targets Windows x64. This report records the local installer before public source hosting was configured. The source is now at [algorithco/algorith-video](https://github.com/algorithco/algorith-video); a signed binary release and update feed remain separate acceptance steps.

## Local artifacts

- Installer: `dist/AlgorithVideo-0.1.0-win-x64.exe`
- Run without installation: `dist/win-unpacked/AlgorithVideo.exe`
- Installer size: 252,784,221 bytes
- Installer SHA256: `48fd02a6d6be2a47743bfc465b44a048088f6cee7fc65cc537330eb6aad71ee1`
- Signing status: unsigned; no Algorithco signing certificate is configured.

The NSIS installer supports per-user installation and choosing the install directory. The package includes standalone Python 3.12.14, locked Python dependencies, FFmpeg/FFprobe and a native yt-dlp launcher. Runtime licenses and provenance records are bundled.

## Verification

- TypeScript typecheck and lint passed.
- Release tests passed: 25 passed, 2 skipped; branding checks passed.
- The actual packaged runtime passed verification after copying resources to a path containing spaces. Checks covered smart rendering, transcription audio extraction, yt-dlp, H.264 output, captions, speed changes, audio synchronization, editor movement and the face model.
- The actual packaged GUI passed with an isolated profile and system Python/media tools removed from PATH. All eight system checks passed, the About page displayed AlgorithVideo 0.1.0 by Algorithco, and automatic updates reported `not-configured`.
- Installer archive integrity passed. Windows executable metadata identifies AlgorithVideo, version 0.1.0, company Algorithco and AMD64 architecture.
- The packaged desktop application was launched successfully with the normal user profile.

GUI acceptance details are in the local `dist/windows-acceptance.json`. Current screenshots are [Create](assets/algorithvideo-create.png) and [About](assets/algorithvideo-about.png).

These checks did not execute the installer or make a paid live AI request. Earlier full application and engine regression results remain in the historical [rebranding verification](ALGORITHVIDEO_REBRANDING_VERIFICATION.md). Build instructions are in [Windows packaging](RELEASING.md).
