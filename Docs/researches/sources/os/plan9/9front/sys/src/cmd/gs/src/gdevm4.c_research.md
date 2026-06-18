# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm4.c

Implements the 4-bit `image4` mapped-color memory device and little-endian `image4w` variant.

Key behavior:
- Registers `mem_mapped4_device` with mapped RGB map/unmap, copy, fill, and gray strip-copy ROP.
- Defines 16 precomputed fill patterns where each nibble repeats the color value.
- `mem_mapped4_fill_rectangle` fills bit ranges with `bits_fill_rectangle`, scaling x/w by 4 bits per pixel.
- `mem_mapped4_copy_mono` handles transparent-noop, masked, reverse-masked, and opaque cases.
- Opaque bitmap copy builds a four-entry table for all two-source-bit combinations and processes aligned destination nibbles in pairs.
- Masked copy toggles high/low nibble masks as it walks pixels.
- `mem_mapped4_copy_color` temporarily quadruples `dev->width` and delegates to monobit copy logic.
- Little-endian `mem_mapped4_word_device` wraps operations with `mem_swap_byte_rect`.

Dependencies and notes:
- Like `gdevm2.c`, this file reuses `mem_mono_device` or `mem_mono_word_device` for color bitmap copies by widening coordinate space.
