# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmr8n.c

## Role

RasterOp implementation for 8-bit gray and 24-bit RGB memory devices.

## Main Function

- `mem_gray8_rgb24_strip_copy_rop`

## Main Behavior

- Supports 8-bit destination pixels and 24-bit destination pixels, using `bpp = depth >> 3`.
- Detects constant source and texture cases and simplifies RasterOps when source or texture equals device black/white.
- For non-grayscale 8-bit devices, supports only simple constant, destination, source, or texture cases; otherwise falls back to `mem_default_strip_copy_rop`.
- Handles transparency by skipping pixels matching transparent source/texture sentinel values.
- Splits execution into cases:
  - constant source and constant texture
  - data source and constant texture
  - constant source and data texture
  - data source and data texture
- Supports 1-bit source/texture via color tables and multi-byte source/texture for 8/24-bit data.

## Limitations

The file comments state that 16-bit and 32-bit cases are not implemented and fall back to the slow default implementation.

## Risks and Edge Cases

- The data-source/data-texture 8-bit path mixes pointer increments and bit-index logic; correctness depends on whether `scolors`/`tcolors` indicate 1-bit data.
- 24-bit pixels are packed as `R,G,B` in memory and converted to/from `gx_color_index` with local macros.
