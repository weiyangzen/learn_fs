# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm48.c

Implements the 48-bit `image48` true-color memory device and little-endian `image48w` variant.

Key behavior:
- Registers `mem_true48_device` with 6-byte pixels, RGB map/unmap, copy, fill, default alpha copy, strip-copy ROP, and get-bits support.
- Unpacks `gx_color_index` into six component bytes.
- Maintains a three-word color cache for repeated 48-bit color patterns (`abcd`, `cdef`, `efab`) with endian-specific layouts.
- `mem_true48_fill_rectangle` handles repeated-byte grayscale fills, cached wide color fills, and narrow fills.
- Since two 6-byte pixels make three 32-bit words, the wide fill path writes two pixels per loop.
- `mem_true48_copy_mono` provides explicit-color and stencil paths.
- `mem_true48_copy_color` delegates to `mem_copy_byte_rect`.
- Little-endian `mem_true48_word_device` swaps byte rectangles around all write paths.

Dependencies and notes:
- Similar to `gdevm40.c`, but its pixel size naturally groups as two pixels per 12-byte block.
