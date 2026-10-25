'use strict'
const { test } = require('node:test')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const { buildApp, launchApp, ROOT } = require('../zernio/support/electron-app.cjs')
const { linkEngine } = require('./editor-e2e-tools.cjs')

test('AlgorithVideo opens with the supplied logo, new API and public project links', async (t) => {
  const scratch = fs.mkdtempSync(path.join(os.tmpdir(), 'algorithvideo-brand-e2e-'))
  let session
  t.after(async () => {
    if (session) {
      session.app.process().kill()
      await session.close()
    }
    assert.equal(path.dirname(path.resolve(scratch)), path.resolve(os.tmpdir()))
    fs.rmSync(scratch, { recursive: true, force: true, maxRetries: 5, retryDelay: 100 })
  })
  const appDir = buildApp(path.join(scratch, 'app'))
  linkEngine(appDir)
  fs.symlinkSync(path.join(ROOT, 'build'), path.join(appDir, 'build'), 'junction')
  session = await launchApp({ appDir, userDataDir: path.join(scratch, 'profile') })
  const { page } = session
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.addStyleTag({ content: '*, *::before, *::after { animation: none !important; transition: none !important; }' })
  const capture = async (name) => {
    await page.evaluate(() => document.fonts.ready.then(() => true))
    const png = await session.app.evaluate(async ({ BrowserWindow }) => {
      const window = BrowserWindow.getAllWindows()[0]
      window.webContents.setBackgroundThrottling(false)
      await window.capturePage(undefined, { stayHidden: true, stayAwake: true })
      await new Promise((resolve) => setTimeout(resolve, 180))
      const frame = await window.capturePage(undefined, { stayHidden: true, stayAwake: true })
      return frame.toPNG().toString('base64')
    })
    const bytes = Buffer.from(png, 'base64')
    assert.ok(bytes.length > 1000, 'the hidden window produced a rendered frame')
    fs.writeFileSync(path.join(process.env.ALGORITHVIDEO_SCREENSHOT_DIR, name), bytes)
  }
  const product = await session.app.evaluate(({ app, BrowserWindow }) => ({ name: app.getName(), title: BrowserWindow.getAllWindows()[0].getTitle() }))
  assert.equal(product.name, 'AlgorithVideo')
  assert.equal(product.title, 'AlgorithVideo')
  const identity = await page.evaluate(() => ({
    api: typeof window.algorithvideo.settings.load,
    legacyApi: typeof window.bridgeclip,
    accent: getComputedStyle(document.documentElement).getPropertyValue('--accent').trim(),
    ink: getComputedStyle(document.documentElement).getPropertyValue('--accent-ink').trim()
  }))
  assert.equal(identity.api, 'function')
  assert.equal(identity.legacyApi, 'undefined')
  assert.equal(identity.accent, '255 213 0')
  assert.equal(identity.ink, '10 10 10')
  await page.waitForFunction(() => [...document.querySelectorAll('img[alt="AlgorithVideo"]')].some((image) => image.complete && image.naturalWidth > 0))
  const screenshots = process.env.ALGORITHVIDEO_SCREENSHOT_DIR
  if (screenshots) {
    fs.mkdirSync(screenshots, { recursive: true })
    await capture('algorithvideo-create.png')
  }
  await page.getByRole('button', { name: 'Settings', exact: true }).evaluate((button) => button.click())
  assert.match(await page.locator('body').innerText(), /Developed by Algorithco/)
  assert.equal(await page.getByRole('button', { name: 'GitHub', exact: true }).count(), 1)
  assert.equal(await page.getByRole('button', { name: 'Report an issue', exact: true }).count(), 1)
  const update = await page.evaluate(() => window.algorithvideo.update.getState())
  assert.equal(update.status, 'off')
  assert.ok(['development', 'not-configured'].includes(update.reason))
  await page.getByRole('button', { name: 'About', exact: true }).evaluate((button) => button.click())
  await page.waitForFunction(() => document.getElementById('settings-about').getBoundingClientRect().bottom <= window.innerHeight)
  assert.equal(await page.evaluate(() => window.scrollY), 0, 'About navigation keeps the application shell fixed')
  assert.equal(await page.evaluate(() => document.querySelector('aside').getBoundingClientRect().top), 0)
  if (screenshots) await capture('algorithvideo-about.png')
  const content = await page.locator('body').innerText()
  assert.doesNotMatch(content, /bridgeclip|bridge[- ]?mind/i)
})
