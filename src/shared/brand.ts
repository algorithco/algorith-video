// Product identity and public project links.
export const APP_NAME = 'AlgorithVideo'
export const COMPANY_NAME = 'Algorithco'
export const APP_TAGLINE = 'Turn long videos into your next story'
export const APP_ID = 'com.algorithco.algorithvideo'

export const COMPANY_URL: string = 'https://github.com/algorithco'
export const REPO_URL: string = 'https://github.com/algorithco/algorith-video'
export const ISSUES_URL = REPO_URL ? `${REPO_URL}/issues` : ''
export const RELEASES_URL = REPO_URL ? `${REPO_URL}/releases` : ''
export const LICENSE_NAME = 'MIT'

// Source hosting is configured; signed binary updates remain disabled.
// Configure these together with electron-builder.yml before enabling updates.
export const RELEASE_REPOSITORY: { owner: string; repo: string } | null = null
export const MAC_SIGNING_TEAM_ID: string = ''

export const PROVIDER_LINKS = {
  openrouter: 'https://openrouter.ai/keys',
  zernio: 'https://zernio.com/dashboard/api-keys'
} as const

export const ZERNIO_LINKS = {
  signup: 'https://zernio.com/signup',
  pricing: 'https://zernio.com/pricing',
  billing: 'https://zernio.com/dashboard/billing'
} as const
