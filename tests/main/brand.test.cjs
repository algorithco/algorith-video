'use strict'
const assert = require('node:assert/strict')
const { test } = require('node:test')
const fs = require('node:fs')
const path = require('node:path')
const crypto = require('node:crypto')
const root = path.resolve(__dirname, '../..')

test('product metadata links the public Algorithco repository and keeps binary publishing disabled', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'))
  const lock = JSON.parse(fs.readFileSync(path.join(root, 'package-lock.json'), 'utf8'))
  assert.equal(pkg.name, 'algorithvideo')
  assert.equal(pkg.productName, 'AlgorithVideo')
  assert.equal(pkg.author, 'Algorithco')
  assert.equal(pkg.version, '0.1.0')
  assert.equal(pkg.license, 'MIT')
  assert.equal(pkg.homepage, 'https://github.com/algorithco/algorith-video#readme')
  assert.deepEqual(pkg.repository, { type: 'git', url: 'git+https://github.com/algorithco/algorith-video.git' })
  assert.deepEqual(pkg.bugs, { url: 'https://github.com/algorithco/algorith-video/issues' })
  assert.equal(lock.name, pkg.name)
  assert.equal(lock.version, pkg.version)
  assert.equal(lock.packages[''].name, pkg.name)
  assert.equal(lock.packages[''].version, pkg.version)
  const config = require('js-yaml').load(fs.readFileSync(path.join(root, 'electron-builder.yml'), 'utf8'))
  assert.equal(config.appId, 'com.algorithco.algorithvideo')
  assert.equal(config.productName, pkg.productName)
  assert.equal(config.publish, null)
  assert.equal(config.mac, undefined)
  assert.equal(config.linux, undefined)
  assert.equal(config.dmg, undefined)
  assert.deepEqual(config.win.target, [{ target: 'nsis', arch: ['x64'] }])
  assert.equal(config.win.verifyUpdateCodeSignature, true)
})

test('runtime source cannot regain predecessor identity outside the explicit compatibility layer', () => {
  const files = []
  const scan = (directory) => {
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      if (['.venv', '__pycache__', '.pytest_cache'].includes(entry.name)) continue
      const full = path.join(directory, entry.name)
      if (entry.isDirectory()) scan(full)
      else if (/\.(ts|tsx|py|css|html)$/.test(entry.name) && entry.name !== 'legacy-brand.ts') files.push(full)
    }
  }
  for (const directory of ['src', 'bridge', 'engine/clip_engine']) scan(path.join(root, directory))
  for (const file of files) assert.doesNotMatch(fs.readFileSync(file, 'utf8'), /bridgeclip|bridge[- ]?mind|9CBJCDR3J2/i, path.relative(root, file))
})

test('the supplied logo is preserved and all shipping brand assets use it', () => {
  const source = fs.readFileSync(path.join(root, 'resources/algorithvideo-logo-source.png'))
  assert.equal(crypto.createHash('sha256').update(source).digest('hex'), 'a9743c645fb6fd27619c29897305c56647a55ba19da92784dc0e9b4a4d59616a')
  for (const name of ['algorithvideo-mark.svg', 'algorithvideo-logo.svg', 'algorithvideo-logo-light.svg']) {
    const svg = fs.readFileSync(path.join(root, 'resources', name), 'utf8')
    assert.match(svg, /aria-label="AlgorithVideo"/)
    const data = /data:image\/png;base64,([^"\s]+)/.exec(svg)
    assert.ok(data, name)
    assert.equal(crypto.createHash('sha256').update(Buffer.from(data[1], 'base64')).digest('hex'), crypto.createHash('sha256').update(source).digest('hex'), name)
  }
  const ico = fs.readFileSync(path.join(root, 'build/icon.ico'))
  assert.equal(ico.readUInt16LE(2), 1)
  assert.equal(ico.readUInt16LE(4), 7)
  assert.equal(fs.readFileSync(path.join(root, 'build/icon.icns')).subarray(0, 4).toString(), 'icns')
})
