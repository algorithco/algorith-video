'use strict'
// First desktop release: verified native installers, no automatic update feed.
const fs = require('node:fs')
const path = require('node:path')
const crypto = require('node:crypto')

const targets = {
  'windows-x64': { os: 'win', arch: 'x64', extensions: ['exe'] },
  'mac-arm64': { os: 'mac', arch: 'arm64', extensions: ['dmg', 'zip'] },
  'mac-x64': { os: 'mac', arch: 'x64', extensions: ['dmg', 'zip'] },
  'linux-x64': { os: 'linux', arch: 'x64', extensions: ['AppImage', 'deb'] }
}

function sha256(file, combined) {
  const hash = crypto.createHash('sha256'), buffer = Buffer.alloc(1024 * 1024)
  const descriptor = fs.openSync(file, 'r')
  try {
    let read
    while ((read = fs.readSync(descriptor, buffer, 0, buffer.length, null)) > 0) {
      const chunk = buffer.subarray(0, read)
      hash.update(chunk)
      if (combined) combined.update(chunk)
    }
    return hash.digest('hex')
  } finally { fs.closeSync(descriptor) }
}

function sourceAssets(directory, archive, reconstruction) {
  if (!archive || !/^ffmpeg-sources-windows-linux\.tar\.(xz|gz)$/.test(archive.name)
    || !Number.isSafeInteger(archive.size) || archive.size <= 0 || !/^[a-f0-9]{64}$/.test(archive.sha256)) throw new Error('Invalid corresponding-source archive')
  const parts = archive.parts === undefined ? [{ name: archive.name, size: archive.size, sha256: archive.sha256 }] : archive.parts
  if (!Array.isArray(parts) || parts.length === 0) throw new Error('Missing corresponding-source archive parts')
  const combined = crypto.createHash('sha256'), inputs = []
  let total = 0
  for (const [index, part] of parts.entries()) {
    const expectedName = archive.parts === undefined ? archive.name : `${archive.name}.part${String(index + 1).padStart(2, '0')}`
    if (!part || part.name !== expectedName || !Number.isSafeInteger(part.size) || part.size <= 0 || part.size >= 2_000_000_000
      || !/^[a-f0-9]{64}$/.test(part.sha256)) throw new Error('Invalid corresponding-source archive part')
    const file = path.join(directory, part.name)
    if (!fs.lstatSync(file).isFile() || fs.statSync(file).size !== part.size || sha256(file, combined) !== part.sha256) throw new Error('Corresponding-source archive hash mismatch')
    inputs.push({ file, name: part.name })
    total += part.size
  }
  if (total !== archive.size || combined.digest('hex') !== archive.sha256) throw new Error('Combined corresponding-source archive hash mismatch')
  if (archive.parts !== undefined) {
    const name = 'SOURCE-RECONSTRUCTION.txt', file = path.join(directory, name)
    if (!reconstruction || reconstruction.name !== name || !Number.isSafeInteger(reconstruction.size) || reconstruction.size <= 0
      || !/^[a-f0-9]{64}$/.test(reconstruction.sha256) || !fs.lstatSync(file).isFile()
      || fs.statSync(file).size !== reconstruction.size || sha256(file) !== reconstruction.sha256) throw new Error('Invalid source reconstruction instructions')
    inputs.push({ file, name })
  }
  return inputs
}

function collect(root, output, version, sourceSha) {
  if (!/^\d+\.\d+\.\d+$/.test(version) || !/^[a-f0-9]{40}$/.test(sourceSha)) throw new Error('Invalid release identity')
  if (fs.existsSync(output)) throw new Error('Publication directory already exists')
  const inputs = []
  const sourceDirectory = path.join(root, 'media-sources')
  const sourceManifestFile = path.join(sourceDirectory, 'source-manifest.json')
  const sourceManifest = JSON.parse(fs.readFileSync(sourceManifestFile, 'utf8'))
  const lock = require('./runtime-lock.json')
  if (sourceManifest.recipe_commit !== lock.ffmpeg.windows.build_commit || sourceManifest.ffmpeg_commit !== lock.ffmpeg.source_commit) throw new Error('Wrong corresponding-source revision')
  const archive = sourceManifest.archive
  inputs.push(...sourceAssets(sourceDirectory, archive, sourceManifest.reconstruction), { file: sourceManifestFile, name: 'ffmpeg-source-manifest.json' })
  for (const [target, contract] of Object.entries(targets)) {
    const directory = path.join(root, target)
    const evidence = JSON.parse(fs.readFileSync(path.join(directory, `verification-${target}.json`), 'utf8'))
    if (evidence.target !== target || evidence.version !== version || evidence.sourceSha !== sourceSha || !evidence.runtimeVerified || !evidence.guiVerified) {
      throw new Error(`Invalid ${target} native verification`)
    }
    for (const extension of contract.extensions) {
      const name = `AlgorithVideo-${version}-${contract.os}-${contract.arch}.${extension}`
      const file = path.join(directory, name)
      if (!fs.lstatSync(file).isFile() || fs.statSync(file).size === 0) throw new Error(`Missing installer ${name}`)
      inputs.push({ file, name })
    }
    if (target.startsWith('mac-') && !fs.existsSync(path.join(directory, `ffmpeg-sources-${target}.tar.gz`))) throw new Error(`Missing ${target} library sources`)
    for (const name of fs.readdirSync(directory)) {
      if (/^(verification-|node-sbom-|python-packages-)[a-z0-9-]+\.json$/.test(name) || /^ffmpeg-sources-[a-z0-9-]+\.tar\.(xz|gz)$/.test(name)) {
        const file = path.join(directory, name)
        if (!fs.lstatSync(file).isFile()) throw new Error('Release evidence is not a regular file')
        inputs.push({ file, name })
      }
    }
  }
  if (new Set(inputs.map(item => item.name)).size !== inputs.length) throw new Error('Duplicate release asset')
  fs.mkdirSync(output)
  for (const item of inputs) fs.copyFileSync(item.file, path.join(output, item.name), fs.constants.COPYFILE_EXCL)
  const files = inputs.map(item => ({ name: item.name, size: fs.statSync(item.file).size, sha256: sha256(item.file) })).sort((a, b) => a.name.localeCompare(b.name))
  const manifest = { product: 'AlgorithVideo', version, sourceRepository: 'https://github.com/algorithco/algorith-video', sourceSha, builtBy: 'GitHub Actions native runners', automaticUpdates: false, signing: 'Windows/Linux unsigned; macOS ad-hoc, not notarized', files }
  const manifestPath = path.join(output, 'release-manifest.json')
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + '\n')
  fs.writeFileSync(path.join(output, 'SHA256SUMS.txt'), files.map(file => `${file.sha256}  ${file.name}\n`).join('') + `${sha256(manifestPath)}  release-manifest.json\n`)
  return manifest
}

if (require.main === module) {
  try { collect(...process.argv.slice(2)) } catch (error) { console.error(error.message); process.exitCode = 1 }
}
module.exports = { collect, targets }
