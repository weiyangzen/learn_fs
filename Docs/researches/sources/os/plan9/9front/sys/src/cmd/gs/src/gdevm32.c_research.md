# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm32.c

Implements the 32-bit `image32` memory device and little-endian `image32w` variant.

Key behavior:
- Registers `mem_true32_device` as a 32-bit storage format with 24 color bits and 8 alpha/extra bits.
- Uses endian-aware `arrange_bytes` and `color_swap_bytes` to store 32-bit pixel words in the expected byte order.
- `mem_true32_fill_rectangle` optimizes widths 1 through 4, zero fills via `memset`, and wider repeated 32-bit stores.
- `mem_true32_copy_mono` has a fast stencil path for transparent `zero` and real `one`, unrolling full source bytes into up to eight destination pixels.
- The nontransparent-zero path handles explicit zero/one colors pixel by pixel.
- `mem_true32_copy_color` uses `mem_copy_byte_rect`.
- Little-endian `mem_true32_word_device` wraps color values with byte swapping and swaps copied color rectangles for word-oriented output.

Dependencies and notes:
- Uses `gx_default_map_rgb_color`, `gx_default_map_color_rgb`, and `gx_default_cmyk_map_cmyk_color`.
- The word variant’s `copy_color` copies raw bytes and then calls `mem_swap_byte_rect`.
