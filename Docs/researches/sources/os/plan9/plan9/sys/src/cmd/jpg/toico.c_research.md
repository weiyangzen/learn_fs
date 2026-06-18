# File Research: sources/os/plan9/plan9/sys/src/cmd/jpg/toico.c

## Purpose
Converts Plan 9 images to a Microsoft ICO file.

## Behavior
Reads each input image, converts non-indexed images to 8-bit grey or CMAP8, computes used colors, minimizes output bit depth to 1/2/4/8 bits, and writes ICO file header, icon directory entries, BMP-like icon headers, color maps, XOR masks, and AND masks.

## Notes
Rows are padded to 32-bit boundaries and stored bottom-up. Transparent mask generation treats pixel value `0xff` as transparent in the AND mask logic.
