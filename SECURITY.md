# Security policy

AlgorithVideo is maintained by Algorithco. Please report suspected vulnerabilities privately so a fix can be prepared before technical details become public.

## Supported versions

| Version | Security updates |
| --- | --- |
| Latest `0.1.x` release | Supported |
| Earlier patches and other versions | Upgrade to the latest supported release |

The project is in early development. Fixes are normally made against the current source and latest supported release; older patches are not maintained separately.

## Report a vulnerability

Use [GitHub's private vulnerability reporting form](https://github.com/algorithco/algorith-video/security/advisories/new), or open the repository's **Security** tab and select **Report a vulnerability**. Reports are shared privately with the repository maintainers.

Include enough information to reproduce the problem safely:

- The affected AlgorithVideo version or commit, operating system and relevant feature.
- Reproduction steps, expected behavior and actual behavior.
- The security impact and any prerequisites for exploitation.
- A small synthetic fixture or proof of concept when possible.
- Sanitized logs or screenshots that help explain the issue.

Do not attach real API keys, session tokens, private videos, account credentials or unredacted application data. Replace sensitive values with clearly marked placeholders. If a credential has already been exposed, revoke or rotate it with the relevant provider.

Do not disclose a suspected vulnerability in a public issue or pull request before discussing it with maintainers. If the private form is unavailable, email [otashdev1@gmail.com](mailto:otashdev1@gmail.com). Start with a short description and arrange a safe way to share sensitive evidence; do not email working credentials or private media.

Maintainers will review reports, ask for clarification when needed and coordinate fixes and disclosure with the reporter. Response time depends on severity and maintainer availability; the project does not promise a fixed response deadline. Reporters are welcome to follow up in the private report.

Ordinary bugs and feature requests belong in [GitHub Issues](https://github.com/algorithco/algorith-video/issues).

## Security and privacy boundaries

- The Electron renderer is sandboxed and does not receive saved provider keys. Electron main validates IPC requests and authorizes access to local media.
- API keys are stored using the operating system's secure storage. Keep keys out of source files, issue reports, screenshots and logs.
- The Python engine treats downloaded media, saved library files and provider responses as untrusted input. Network destination checks and media subprocess restrictions must be preserved.
- Rendering runs locally, while transcription, planning and enabled visual analysis send data to external AI providers. Social publishing uploads selected clips through Zernio. See [AI, costs and privacy](docs/ai-and-privacy.md) for the data flow.
- Native runtime packaging, signing and update verification have separate acceptance requirements in [the release guide](docs/RELEASING.md). A passing source CI run does not certify an installer.

This policy covers the AlgorithVideo code in this repository. Vulnerabilities in OpenRouter, Zernio, social platforms or installed assistant CLIs should also be reported to the service or project's own security team when appropriate.
