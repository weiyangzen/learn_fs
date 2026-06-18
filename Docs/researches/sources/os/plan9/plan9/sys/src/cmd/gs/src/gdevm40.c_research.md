# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm40.c

Implements 40-bit memory devices `image40` and little-endian `image40w`. Pixels are five bytes, using default RGB mapping and alpha-capable memory device setup.

The implementation follows the high-depth memory-device template: unpack color bytes, cache rotated 32-bit word patterns in `mdev->color40`, optimize grayscale fills with `memset`, handle narrow widths directly, and fill wide non-gray rectangles with repeated cached words.

`mem_true40_copy_mono` supports full opaque and stencil-style mono copies into 5-byte pixels. `mem_true40_copy_color` delegates to `mem_copy_byte_rect`.

The word-oriented variant swaps bit ranges with `mem_swap_byte_rect` before and after fill/copy and uses direct byte-copy for color data.

The unusual 5-byte stride creates more rotated-cache state than 24/48-bit devices; correctness depends on endian-specific cache macros.
