# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm40.c

Implements the 40-bit `image40` true-color memory device and little-endian `image40w` variant.

Key behavior:
- Registers `mem_true40_device` with 5-byte pixels, RGB map/unmap, copy, fill, default alpha copy, and get-bits support.
- Unpacks 64-bit `gx_color_index` values into five bytes.
- Uses `mdev->color40` to cache endian-specific 32-bit word rotations for repeated 5-byte color patterns.
- `mem_true40_fill_rectangle` optimizes grayscale repeated-byte fills with `memset`, cached wide color fills, and narrow fills of width 1 through 4.
- `mem_true40_copy_mono` mirrors the 24-bit stencil structure but writes five bytes per destination pixel.
- `mem_true40_copy_color` delegates to `mem_copy_byte_rect`.
- Little-endian `mem_true40_word_device` swaps byte rectangles around fill, mono copy, and color copy operations.

Dependencies and notes:
- Uses `uint64_t` color extraction.
- The cache stores five rotated 32-bit words (`abcd`, `bcde`, `cdea`, `deab`, `eabc`) to make 5-byte pixels efficient despite unaligned word boundaries.
