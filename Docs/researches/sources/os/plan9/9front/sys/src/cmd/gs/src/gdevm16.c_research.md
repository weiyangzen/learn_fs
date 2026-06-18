# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm16.c

Implements the 16-bit `image16` true-color memory device using RGB565 layout.

Key behavior:
- Registers `mem_true16_device` with custom RGB map/unmap, mono copy, color copy, fill, and default strip-copy ROP.
- `mem_true16_map_rgb_color` packs color values as 5 red bits, 6 green bits, and 5 blue bits.
- `mem_true16_map_color_rgb` expands 5/6-bit components back into Ghostscript color values.
- Pixels are stored in big-endian byte order; little-endian hosts byte-swap the 16-bit color for memory writes.
- `mem_true16_fill_rectangle` optimizes single-pixel, repeated-byte colors, and wider nonuniform fills.
- `mem_true16_copy_mono` applies transparent or explicit zero/one colors pixel by pixel.
- `mem_true16_copy_color` delegates rectangular byte copying to `mem_copy_byte_rect`.

Dependencies and notes:
- Uses `mem_device("image16", 16, 0, ...)`.
- Unlike many neighboring files, it does not define a separate `image16w` word-oriented variant.
