// Compatibility only: earlier local clip libraries keep these marker names.
// New records use the AlgorithVideo namespace. Never expose these in the UI.
export const LEGACY_LIBRARY_FAVORITE_FILE = '.bridgeclip-favorite'
export const legacyManualPostedFile = (clipIndex: number): string => `.bridgeclip-posted-${clipIndex}`
