// Cross-platform export of the original AlgorithVideo brand artwork.
const { execFileSync } = require('node:child_process')
const { existsSync } = require('node:fs')
const path = require('node:path')
const localPython = path.join(__dirname, '.venv', ...(process.platform === 'win32' ? ['Scripts', 'python.exe'] : ['bin', 'python']))
const python = process.env.PYTHON || (existsSync(localPython) ? localPython : process.platform === 'win32' ? 'python' : 'python3')
execFileSync(python, [path.join(__dirname, 'export-assets.py')], { stdio: 'inherit', windowsHide: true })
