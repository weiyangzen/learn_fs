# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm1.c

Implements the 1-bit `image1` monobit memory device and, on little-endian hosts, the `image1w` word-oriented variant.

Key behavior:
- Registers `mem_mono_device` with custom RGB mapping, mono copy, fill, strip-tile, strip-copy ROP, and get-bits support.
- Color mapping accounts for possible inverted palette data in `mdev->palette.data[0]`.
- `mem_mono_fill_rectangle` uses `bits_fill_rectangle`, unless `USE_COPY_ROP` is enabled for test coverage through ROP code.
- `mem_mono_copy_mono` is a performance-heavy implementation with architecture-dependent chunk fetch macros.
- Handles transparent, zero, and one color combinations via a `copy_modes` lookup table mapping to OR, STORE, AND, or fallback behavior.
- Optimizes single-chunk, one-source-to-two-destination chunks, aligned multi-chunk, and unaligned multi-chunk copies separately.
- `mem_mono_strip_tile_rectangle` reimplements monochrome halftone strip tiling for performance when colors are complements and tile shift is zero; otherwise delegates to `gx_default_strip_tile_rectangle`.
- Little-endian `mem_mono_word_device` wraps fills and copies with `mem_swap_byte_rect` and uses `mem_word_get_bits_rectangle`.

Dependencies and notes:
- Core dependency is `gdevmem.h` for scan-line, fit, chunk, mask, and swap helpers.
- The file contains a comment noting `mem_mono_map_color_rgb` is unusual because map-color procedures normally return an error code.
- The code is highly sensitive to bit order, chunk alignment, and host endian configuration.
