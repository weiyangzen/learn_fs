# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm2.c

Implements the 2-bit `image2` mapped-color memory device and little-endian `image2w` variant.

Key behavior:
- Registers `mem_mapped2_device` with mapped-color RGB map/unmap, copy, fill, and gray strip-copy ROP.
- Uses four precomputed 2-bit fill patterns for color values 0 through 3.
- `mem_mapped2_fill_rectangle` fills bit ranges with `bits_fill_rectangle`, scaling x/w by 2 bits per pixel.
- `mem_mapped2_copy_mono` handles opaque bitmaps, stencils, and reverse stencils using nibble/bit masks.
- `mem_mapped2_copy_color` temporarily doubles `dev->width` and reuses `mem_mono_device.copy_mono` over expanded bit coordinates.
- Little-endian `mem_mapped2_word_device` wraps fill/copy operations with `mem_swap_byte_rect` and uses `mem_word_get_bits_rectangle`.

Dependencies and notes:
- Relies on `mem_mapped_map_rgb_color` and `mem_mapped_map_color_rgb`, defined elsewhere in the memory-device layer.
- The temporary `dev->width` mutation is local and restored immediately after delegation.
