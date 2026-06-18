# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm2.c

Implements 2-bit mapped-color memory devices `image2` and, on little-endian systems, `image2w`. The standard device stores four 2-bit pixels per byte.

`mem_mapped2_fill_rectangle` uses `bits_fill_rectangle` with precomputed fill patterns for color indices 0 to 3. `mem_mapped2_copy_mono` handles opaque and transparent monochrome source copies into 2-bit destinations with nibble-pair masks.

`mem_mapped2_copy_color` temporarily scales `dev->width` and delegates to the monobit memory device’s `copy_mono`, treating 2-bit pixels as paired bits for bulk copying.

The word-oriented variant wraps standard operations with byte swapping through `mem_swap_byte_rect`, then uses `mem_mono_word_device` for color copies.

This file depends on shared mapped-color mapping procedures (`mem_mapped_map_rgb_color`, `mem_mapped_map_color_rgb`) and low-level bit rectangle helpers.
