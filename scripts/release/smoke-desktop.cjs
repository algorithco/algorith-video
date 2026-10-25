'use strict'
// Runs only on native GitHub runners; uses isolated settings and no provider keys.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const { spawn } = require('node:child_process')
const { chromium } = require('playwright-core')
const pause = ms => new Promise(resolve => setTimeout(resolve, ms))

async function main() {
  assert.equal(process.env.GITHUB_ACTIONS, 'true', 'Native release acceptance runs on GitHub Actions only.')
  const [appDirectory, target] = process.argv.slice(2)
  assert.ok(['windows-x64', 'linux-x64', 'mac-arm64', 'mac-x64'].includes(target), 'Unknown desktop target')
  const root = path.resolve(__dirname, '../..')
  const version = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8')).version
  const directory = path.resolve(appDirectory)
  const executable = path.join(directory, process.platform === 'darwin' ? 'Contents/MacOS/AlgorithVideo' : process.platform === 'win32' ? 'AlgorithVideo.exe' : 'algorithvideo')
  const resources = path.join(directory, process.platform === 'darwin' ? 'Contents/Resources' : 'resources')
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'AlgorithVideo release acceptance '))
  const profile = path.join(scratch, 'profile'), library = path.join(scratch, 'library')
  fs.mkdirSync(profile)
  fs.writeFileSync(path.join(profile, 'settings.json'), JSON.stringify({ version: 12, openrouterApiKey: '', zernioApiKey: '', outputDirectory: library, pythonPath: 'python', customVocabulary: '', jevEnabled: 'off', jevVisualContext: 'off', sourceContextWebResearch: 'off' }))
  const blocked = new Set(['PATH', 'PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV', 'ELECTRON_RUN_AS_NODE', 'ELECTRON_RENDERER_URL', 'NODE_OPTIONS'])
  const environment = Object.fromEntries(Object.entries(process.env).filter(([key]) => !blocked.has(key.toUpperCase())))
  environment.PATH = process.platform === 'win32' ? `${process.env.SystemRoot}\\system32;${process.env.SystemRoot}` : '/usr/bin:/bin:/usr/sbin:/sbin'
  let child, browser, launchError
  try {
    const args = [`--user-data-dir=${profile}`, '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=0', '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding']
    // The GitHub Ubuntu runner restricts unprivileged user namespaces.
    // This exception is for the isolated synthetic acceptance process only.
    if (process.platform === 'linux') args.push('--no-sandbox')
    child = spawn(executable, args, { env: environment, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] })
    child.once('error', error => { launchError = error })
    let errors = ''
    child.stderr.on('data', chunk => { errors = (errors + chunk.toString()).slice(-8000) })
    child.stdout.resume()
    const portFile = path.join(profile, 'DevToolsActivePort'), deadline = Date.now() + 60000
    while (!fs.existsSync(portFile)) {
      if (launchError) throw new Error(`Packaged app could not start: ${launchError.message}`)
      if (child.exitCode !== null) throw new Error(`Packaged app exited: ${child.exitCode}. ${errors}`)
      if (Date.now() > deadline) throw new Error(`Packaged app did not become ready. ${errors}`)
      await pause(200)
    }
    const port = Number(fs.readFileSync(portFile, 'utf8').split(/\r?\n/)[0])
    browser = await chromium.connectOverCDP(`http://127.0.0.1:${port}`, { timeout: 20000 })
    const context = browser.contexts()[0]
    const page = context.pages().find(item => item.url().includes('index.html')) || context.pages()[0]
    await page.waitForSelector('aside', { timeout: 30000 })
    assert.equal(await page.title(), 'AlgorithVideo')
    assert.equal(await page.evaluate(() => window.algorithvideo.system.isPackaged()), true)
    const tools = await page.evaluate(() => window.algorithvideo.system.checkTools())
    const required = ['python', 'pythonDeps', 'ffmpeg', 'ffmpegCaptions', 'ffprobe', 'ytdlp', 'engine', 'bridgeRunner']
    for (const name of required) assert.equal(tools[name], true, `Missing bundled ${name}`)
    assert.ok(path.resolve(tools.pythonPath).startsWith(resources + path.sep), 'Uses bundled Python')
    const settings = await page.evaluate(() => window.algorithvideo.settings.load())
    assert.equal(path.resolve(settings.outputDirectory), path.resolve(library))
    const update = await page.evaluate(() => window.algorithvideo.update.getState())
    assert.equal(update.status, 'off')
    assert.equal(update.reason, 'not-configured')
    const evidence = { product: 'AlgorithVideo', version, target, sourceSha: process.env.SOURCE_SHA || process.env.GITHUB_SHA, runtimeVerified: true, guiVerified: true, isolatedProfile: true, bundledTools: Object.fromEntries(required.map(name => [name, tools[name]])), automaticUpdates: false, ciSandboxDisabled: process.platform === 'linux' }
    fs.writeFileSync(path.join(root, `dist/verification-${target}.json`), JSON.stringify(evidence, null, 2) + '\n')
    console.log(JSON.stringify(evidence, null, 2))
  } finally {
    if (browser) await browser.close().catch(() => {})
    if (child && child.exitCode === null) { child.kill(); await Promise.race([new Promise(resolve => child.once('exit', resolve)), pause(5000)]) }
    assert.equal(path.dirname(path.resolve(scratch)), path.resolve(os.tmpdir()))
    fs.rmSync(scratch, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 })
  }
}
main().catch(error => { console.error(error); process.exitCode = 1 })
