# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm16.c

Implements the 16-bit true-color memory device `image16`. Pixel format is RGB 5:6:5, stored in big-endian byte order regardless of host endianness.

Color mapping packs red, green, and blue Ghostscript color values into a 16-bit 5/6/5 index. Reverse mapping expands those bit fields back to full `gx_color_value` ranges with bit replication.

Rendering hooks are `mem_true16_fill_rectangle`, `mem_true16_copy_mono`, and `mem_true16_copy_color`. Fill handles one-pixel, repeated-byte, and general 16-bit store cases, swapping byte order on little-endian hosts.

`copy_mono` writes 16-bit pixels for set/unset source bits while respecting transparent `gx_no_color_index` values. `copy_color` delegates to `mem_copy_byte_rect`.

The file is compact but important as the canonical 16-bit packed RGB memory implementation.
