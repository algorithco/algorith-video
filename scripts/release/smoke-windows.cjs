'use strict'
// Acceptance of the actual Windows app with isolated data and no system media/Python tools.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const { spawn } = require('node:child_process')
const { chromium } = require('playwright-core')

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

async function main() {
  assert.equal(process.platform, 'win32', 'Run native Windows acceptance on Windows.')
  const root = path.resolve(__dirname, '../..')
  const appDir = path.resolve(process.argv[2] || path.join(root, 'dist/win-unpacked'))
  const screenshotDir = process.argv[3] ? path.resolve(process.argv[3]) : null
  const executable = path.join(appDir, 'AlgorithVideo.exe')
  assert.ok(fs.existsSync(executable), 'Build the Windows app first.')
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'AlgorithVideo Windows acceptance '))
  const profile = path.join(scratch, 'isolated profile')
  const library = path.join(scratch, 'isolated library')
  fs.mkdirSync(profile)
  fs.writeFileSync(path.join(profile, 'settings.json'), JSON.stringify({ version: 12, openrouterApiKey: '', zernioApiKey: '', outputDirectory: library, pythonPath: 'python', customVocabulary: '', jevEnabled: 'off', jevVisualContext: 'off', sourceContextWebResearch: 'off' }))
  const blocked = new Set(['PATH', 'PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV', 'ELECTRON_RUN_AS_NODE', 'ELECTRON_RENDERER_URL', 'NODE_OPTIONS'])
  const env = Object.fromEntries(Object.entries(process.env).filter(([key]) => !blocked.has(key.toUpperCase())))
  env.PATH = `${process.env.SystemRoot}\\system32;${process.env.SystemRoot}`
  let browser, child
  let errors = ''
  try {
    child = spawn(executable, [`--user-data-dir=${profile}`, '--remote-debugging-address=127.0.0.1', '--remote-debugging-port=0', '--disable-backgrounding-occluded-windows', '--disable-renderer-backgrounding'], { env, windowsHide: true, stdio: ['ignore', 'pipe', 'pipe'] })
    child.stderr.on('data', (chunk) => { errors += chunk.toString() })
    const portFile = path.join(profile, 'DevToolsActivePort')
    const deadline = Date.now() + 45000
    while (!fs.existsSync(portFile)) {
      if (child.exitCode !== null) throw new Error(`Windows app exited before startup: ${child.exitCode}. ${errors.slice(-2000)}`)
      if (Date.now() > deadline) throw new Error(`No renderer debugging endpoint. ${errors.slice(-2000)}`)
      await wait(150)
    }
    const port = Number(fs.readFileSync(portFile, 'utf8').split(/\r?\n/)[0])
    browser = await chromium.connectOverCDP(`http://127.0.0.1:${port}`, { timeout: 15000 })
    const pages = browser.contexts()[0].pages()
    const page = pages.find((item) => item.url().includes('index.html')) || pages[0]
    await page.waitForSelector('aside', { timeout: 30000 })
    await page.emulateMedia({ reducedMotion: 'reduce' })
    await page.addStyleTag({ content: '*, *::before, *::after { animation: none !important; transition: none !important; }' })
    assert.equal(await page.title(), 'AlgorithVideo')
    const packaged = await page.evaluate(() => window.algorithvideo.system.isPackaged())
    assert.equal(packaged, true)
    const tools = await page.evaluate(() => window.algorithvideo.system.checkTools())
    const required = ['python', 'pythonDeps', 'ffmpeg', 'ffmpegCaptions', 'ffprobe', 'ytdlp', 'engine', 'bridgeRunner']
    for (const name of required) assert.equal(tools[name], true, `${name}: ${tools.pythonError || 'packaged tool missing'}`)
    assert.ok(tools.pythonPath.startsWith(path.join(appDir, 'resources')), 'Python comes from the app resources.')
    const settings = await page.evaluate(() => window.algorithvideo.settings.load())
    assert.equal(path.resolve(settings.outputDirectory), path.resolve(library))
    assert.match(await page.locator('aside').innerText(), /v0\.1\.0/)
    if (screenshotDir) {
      fs.mkdirSync(screenshotDir, { recursive: true })
      await page.screenshot({ path: path.join(screenshotDir, 'algorithvideo-create.png'), animations: 'disabled', timeout: 20000 })
    }
    await page.getByRole('button', { name: 'Settings', exact: true }).click()
    await page.getByRole('button', { name: 'About', exact: true }).click()
    await page.waitForFunction(() => document.getElementById('settings-about').getBoundingClientRect().bottom <= innerHeight)
    assert.match(await page.locator('#settings-about').innerText(), /AlgorithVideo[\s\S]*v0\.1\.0[\s\S]*Developed by Algorithco/)
    const update = await page.evaluate(() => window.algorithvideo.update.getState())
    assert.equal(update.status, 'off')
    assert.equal(update.reason, 'not-configured')
    assert.equal(await page.getByRole('button', { name: 'GitHub', exact: true }).count(), 1)
    if (screenshotDir) await page.screenshot({ path: path.join(screenshotDir, 'algorithvideo-about.png'), animations: 'disabled', timeout: 20000 })
    const report = { product: 'AlgorithVideo', version: '0.1.0', target: 'windows-x64', packaged, systemPythonAndMediaPathRemoved: true, tools: Object.fromEntries(required.map((name) => [name, tools[name]])), updates: update.reason, isolatedProfile: true }
    fs.writeFileSync(path.join(root, 'dist/windows-acceptance.json'), JSON.stringify(report, null, 2) + '\n')
    console.log(JSON.stringify(report, null, 2))
  } finally {
    if (browser) await browser.close().catch(() => {})
    if (child && child.exitCode === null) {
      child.kill()
      await Promise.race([new Promise((resolve) => child.once('exit', resolve)), wait(5000)])
    }
    assert.equal(path.dirname(path.resolve(scratch)), path.resolve(os.tmpdir()))
    fs.rmSync(scratch, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 })
  }
}
main().catch((error) => { console.error(error); process.exitCode = 1 })
