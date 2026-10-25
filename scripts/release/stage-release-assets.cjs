'use strict'
const fs = require('node:fs')
const path = require('node:path')
const { targets } = require('./collect-desktop-release.cjs')
const target = process.argv[2]
const contract = targets[target]
if (!contract) throw new Error('Unknown release target')
const { version } = require('../../package.json')
const output = 'release-assets'
if (fs.existsSync(output)) throw new Error('Release asset directory already exists')
fs.mkdirSync(output)
for (const extension of contract.extensions) {
  const name = `AlgorithVideo-${version}-${contract.os}-${contract.arch}.${extension}`
  fs.copyFileSync(path.join('dist', name), path.join(output, name), fs.constants.COPYFILE_EXCL)
}
for (const name of [`verification-${target}.json`, `node-sbom-${target}.json`, `python-packages-${target}.json`]) {
  fs.copyFileSync(path.join('dist', name), path.join(output, name), fs.constants.COPYFILE_EXCL)
}
if (target.startsWith('mac-')) {
  const name = `ffmpeg-sources-${target}.tar.gz`
  fs.copyFileSync(path.join('release-sources', name), path.join(output, name), fs.constants.COPYFILE_EXCL)
}
