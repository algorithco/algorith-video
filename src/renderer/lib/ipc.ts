import type { AlgorithVideoAPI } from '../../preload/index'

declare global {
  interface Window {
    algorithvideo: AlgorithVideoAPI
  }
}

export function getApi(): AlgorithVideoAPI {
  return window.algorithvideo
}
