# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm8.c

Implements the 8-bit `image8` mapped-color memory device and little-endian `image8w` variant.

Key behavior:
- Registers `mem_mapped8_device` with mapped RGB map/unmap, copy, fill, and gray/RGB24 strip-copy ROP.
- `mem_mapped8_fill_rectangle` uses `bytes_fill_rectangle` directly because each pixel is one byte.
- `mem_mapped8_copy_mono` dispatches to three helper routines:
  - `mapped8_copy01` for opaque zero/one coloring.
  - `mapped8_copyN1` for stencil writes where zero is transparent.
  - `mapped8_copy0N` for reverse stencil writes where one is transparent.
- The helper split exists because of bcc32 compiler limitations.
- `mem_mapped8_copy_color` copies source bytes directly with `mem_copy_byte_rect`.
- Little-endian `mem_mapped8_word_device` wraps fill, mono copy, and color copy with `mem_swap_byte_rect`.

Dependencies and notes:
- `mem_gray8_strip_copy_rop` aliases `mem_gray8_rgb24_strip_copy_rop`.
- This is the simplest packed mapped-color memory device because no bit/nibble packing is needed.
