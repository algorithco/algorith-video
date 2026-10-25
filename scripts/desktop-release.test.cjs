'use strict'
const test = require('node:test')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const os = require('node:os')
const crypto = require('node:crypto')
const { collect, targets } = require('./release/collect-desktop-release.cjs')
const runtime = require('./release/runtime-lock.json')

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'algorithvideo-desktop-release-'))
  t.after(() => fs.rmSync(root, { recursive: true, force: true }))
  const sha = 'a'.repeat(40), version = '0.1.0'
  const sources = path.join(root, 'media-sources')
  fs.mkdirSync(sources)
  const name = 'ffmpeg-sources-windows-linux.tar.gz', contents = Buffer.from('synthetic source archive')
  fs.writeFileSync(path.join(sources, name), contents)
  fs.writeFileSync(path.join(sources, 'source-manifest.json'), JSON.stringify({ recipe_commit: runtime.ffmpeg.windows.build_commit, ffmpeg_commit: runtime.ffmpeg.source_commit, archive: { name, size: contents.length, sha256: crypto.createHash('sha256').update(contents).digest('hex') } }))
  for (const [target, contract] of Object.entries(targets)) {
    const directory = path.join(root, target)
    fs.mkdirSync(directory)
    for (const extension of contract.extensions) fs.writeFileSync(path.join(directory, `AlgorithVideo-${version}-${contract.os}-${contract.arch}.${extension}`), `synthetic ${target} ${extension}`)
    fs.writeFileSync(path.join(directory, `verification-${target}.json`), JSON.stringify({ version, target, sourceSha: sha, runtimeVerified: true, guiVerified: true }))
    if (target.startsWith('mac-')) fs.writeFileSync(path.join(directory, `ffmpeg-sources-${target}.tar.gz`), 'synthetic library sources')
  }
  return { root, sha, version, output: path.join(root, 'publish') }
}

test('the first desktop release requires all seven installers, native evidence and media sources', t => {
  const { root, output, version, sha } = fixture(t)
  const manifest = collect(root, output, version, sha)
  assert.equal(manifest.sourceSha, sha)
  assert.equal(manifest.files.filter(item => /\.(exe|dmg|zip|AppImage|deb)$/.test(item.name)).length, 7)
  assert.equal(manifest.automaticUpdates, false)
  assert.ok(manifest.files.some(item => item.name === 'ffmpeg-sources-windows-linux.tar.gz'))
  assert.match(fs.readFileSync(path.join(output, 'SHA256SUMS.txt'), 'utf8'), /release-manifest\.json/)
})

test('missing platforms or verification for another source cannot publish a partial release', t => {
  const { root, output, version, sha } = fixture(t)
  fs.writeFileSync(path.join(root, 'linux-x64/verification-linux-x64.json'), JSON.stringify({ version, target: 'linux-x64', sourceSha: 'b'.repeat(40), runtimeVerified: true, guiVerified: true }))
  assert.throws(() => collect(root, output, version, sha), /Invalid linux-x64 native verification/)
  assert.equal(fs.existsSync(output), false)
})

test('a modified corresponding-source archive prevents release publication', t => {
  const { root, output, version, sha } = fixture(t)
  fs.appendFileSync(path.join(root, 'media-sources/ffmpeg-sources-windows-linux.tar.gz'), 'modified')
  assert.throws(() => collect(root, output, version, sha), /hash mismatch/)
  assert.equal(fs.existsSync(output), false)
})
