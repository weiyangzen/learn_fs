# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevadmp.c

Apple DMP and ImageWriter printer drivers.

Key points:
- Defines four devices:
  - `appledmp` at 120x72 DPI
  - `iwlo` at 160x72 DPI
  - `iwhi` at 160x144 DPI
  - `iwlq` at 320x216 DPI
- `dmp_print_page` selects device type from resolution.
- Allocates input, output, and printer data buffers.
- Initializes printer modes differently for DMP, ImageWriter low/high, and ImageWriter LQ.
- Processes raster data in 8-, 16-, or 24-line groups depending on device type.
- Reverses scanline order for DMP bit ordering, transposes 8x8 blocks, trims blank leading/trailing printer data, and emits device-specific graphics/skip commands.
- Works around ImageWriter formfeed behavior by backing up before formfeed for non-DMP modes.
- Resets printer state and frees buffers.

Dependencies and interactions:
- Depends on `gdevprn.h`.
- Uses Ghostscript printer scanline copy, transpose, and memory allocation helpers.

OS/filesystem relevance:
- Writes printer escape sequences and raster data to `FILE *`.
