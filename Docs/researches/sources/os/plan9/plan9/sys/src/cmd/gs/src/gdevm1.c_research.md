# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm1.c

Implements the 1-bit memory bitmap devices `image1` and, on little-endian builds, `image1w`. These are core Ghostscript stored-bitmap devices for monochrome rendering.

The public device descriptor `mem_mono_device` uses custom RGB mapping, fill, copy-mono, strip-tile, and strip-copy-rop procedures. Color mapping supports inverted palettes by XORing with `mdev->palette.data[0]`.

`mem_mono_copy_mono` is heavily optimized for bit-aligned and unaligned transfers. It chooses copy modes from color0/color1 transparency and value combinations, then uses chunk fetch/write macros for OR, STORE, and AND operations.

`mem_mono_strip_tile_rectangle` reimplements monochrome strip tiling for performance, optimized for non-shifted two-color halftone tiles. It falls back to `gx_default_strip_tile_rectangle` for unsupported strip/phase combinations.

The little-endian word-oriented variant wraps fill/copy operations with `mem_swap_byte_rect` and uses `mem_word_get_bits_rectangle`. The file is central to bitmap performance and has substantial endian-specific logic.
