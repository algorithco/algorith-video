'use strict'
const test = require('node:test')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const os = require('node:os')
const crypto = require('node:crypto')
const { collect, targets } = require('./release/collect-desktop-release.cjs')
const runtime = require('./release/runtime-lock.json')

function fixture(t, split = false) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'algorithvideo-desktop-release-'))
  t.after(() => fs.rmSync(root, { recursive: true, force: true }))
  const sha = 'a'.repeat(40), version = '0.1.0'
  const sources = path.join(root, 'media-sources')
  fs.mkdirSync(sources)
  const name = 'ffmpeg-sources-windows-linux.tar.gz', contents = Buffer.from('synthetic source archive')
  const checksum = value => crypto.createHash('sha256').update(value).digest('hex')
  const archive = { name, size: contents.length, sha256: checksum(contents) }
  let reconstruction
  if (split) {
    archive.parts = [contents.subarray(0, 9), contents.subarray(9)].map((part, index) => {
      const partName = `${name}.part${String(index + 1).padStart(2, '0')}`
      fs.writeFileSync(path.join(sources, partName), part)
      return { name: partName, size: part.length, sha256: checksum(part) }
    })
    const text = 'Concatenate the numbered parts in order, then verify the logical archive hash.\n'
    reconstruction = { name: 'SOURCE-RECONSTRUCTION.txt', size: Buffer.byteLength(text), sha256: checksum(text) }
    fs.writeFileSync(path.join(sources, reconstruction.name), text)
  } else fs.writeFileSync(path.join(sources, name), contents)
  fs.writeFileSync(path.join(sources, 'source-manifest.json'), JSON.stringify({ recipe_commit: runtime.ffmpeg.windows.build_commit, ffmpeg_commit: runtime.ffmpeg.source_commit, archive, reconstruction }))
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

test('split source archives publish every verified part and reconstruction instructions', t => {
  const { root, output, version, sha } = fixture(t, true)
  const manifest = collect(root, output, version, sha)
  assert.ok(manifest.files.some(item => item.name.endsWith('.part01')))
  assert.ok(manifest.files.some(item => item.name.endsWith('.part02')))
  assert.ok(manifest.files.some(item => item.name === 'SOURCE-RECONSTRUCTION.txt'))
  assert.equal(manifest.files.some(item => item.name === 'ffmpeg-sources-windows-linux.tar.gz'), false)
})

test('individually valid source parts must also match the original combined archive digest', t => {
  const { root, output, version, sha } = fixture(t, true)
  const file = path.join(root, 'media-sources/source-manifest.json')
  const manifest = JSON.parse(fs.readFileSync(file, 'utf8'))
  const part = manifest.archive.parts[1], contents = Buffer.alloc(part.size, 42)
  fs.writeFileSync(path.join(root, 'media-sources', part.name), contents)
  part.sha256 = crypto.createHash('sha256').update(contents).digest('hex')
  fs.writeFileSync(file, JSON.stringify(manifest))
  assert.throws(() => collect(root, output, version, sha), /Combined corresponding-source archive hash mismatch/)
  assert.equal(fs.existsSync(output), false)
})

test('missing or reordered source parts cannot publish an incomplete source bundle', t => {
  const { root, output, version, sha } = fixture(t, true)
  const file = path.join(root, 'media-sources/source-manifest.json')
  const manifest = JSON.parse(fs.readFileSync(file, 'utf8'))
  manifest.archive.parts.reverse()
  fs.writeFileSync(file, JSON.stringify(manifest))
  assert.throws(() => collect(root, output, version, sha), /Invalid corresponding-source archive part/)
  manifest.archive.parts.reverse()
  fs.writeFileSync(file, JSON.stringify(manifest))
  fs.unlinkSync(path.join(root, 'media-sources', manifest.archive.parts[1].name))
  assert.throws(() => collect(root, output, version, sha), /ENOENT/)
  assert.equal(fs.existsSync(output), false)
})
