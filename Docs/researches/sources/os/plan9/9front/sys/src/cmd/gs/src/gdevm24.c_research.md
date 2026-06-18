# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm24.c

Implements the 24-bit RGB `image24` memory device and little-endian `image24w` variant.

Key behavior:
- Registers `mem_true24_device` with RGB map/unmap, mono/color copy, optimized fill, alpha copy, strip tiling, strip-copy ROP, and get-bits support.
- Stores pixels as three bytes per pixel, with `x_to_byte(x) = x * 3`.
- `mem_true24_fill_rectangle` has separate paths for wide fills, grayscale-byte fills, cached color fills, and narrow fills of width 1 through 4.
- Maintains a per-device 24-bit color cache (`mdev->color24`) with endian-specific packed word patterns.
- `mem_true24_copy_mono` optimizes the common stencil case where `zero` is transparent and `one` is a real color, processing full source bytes with unrolled bit checks.
- `mem_true24_copy_color` delegates to `mem_copy_byte_rect`.
- `mem_true24_copy_alpha` blends a source alpha map at depth 2 or 4 into existing RGB destination pixels.
- Little-endian `mem_true24_word_device` swaps byte rectangles around fill, mono copy, and color copy operations.

Dependencies and notes:
- `mem_true24_strip_copy_rop` aliases `mem_gray8_rgb24_strip_copy_rop`.
- Optional `USE_MEMSET` and `USE_MEMCPY` paths are present but disabled.
- Debug statistics are compiled only under `DEBUG`.
