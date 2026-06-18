# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/readpng.c

## Purpose
PNG decoder returning one `Rawimage`.

## Format Support
Validates PNG signature and CRCs, parses IHDR, PLTE, IDAT, IEND, skips ancillary chunks, supports deflate/zlib compression, PNG filters None/Sub/Up/Avg/Paeth, non-interlaced and Adam7 interlaced images, and color types 0, 2, 3, 4, and 6.

## Implementation
`zread()` feeds IDAT bytes to `inflatezlib`; `zwrite()` rebuilds scanlines, applies filters, expands bit depths to 8-bit values, maps palettes, and writes CY/CRGB24/CYA16/CRGBA32 packed channel data.

## Limits
Only compression method 0 and filter method 0 are accepted. Unsupported mandatory chunks or invalid CRCs are fatal.
