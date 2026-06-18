# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm4.c

Implements 4-bit mapped-color memory devices `image4` and little-endian `image4w`. Standard storage packs two 4-bit pixels per byte.

`mem_mapped4_fill_rectangle` fills with precomputed byte patterns from color index 0 to 15. `mem_mapped4_copy_mono` separates transparent/masked and opaque cases, with the opaque path processing destination nibbles and source bits in pairs for speed.

`mem_mapped4_copy_color` temporarily scales the device width and delegates to monobit `copy_mono`, treating each 4-bit pixel as four bits.

The word-oriented variant wraps operations in `mem_swap_byte_rect` and delegates color-copy work to `mem_mono_word_device`.

This file is the 4-bit counterpart to `gdevm2.c`, with more complex nibble alignment handling.
