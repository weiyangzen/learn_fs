# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm56.c

Implements the 56-bit `image56` true-color memory device and little-endian `image56w` variant.

Key behavior:
- Registers `mem_true56_device` with 7-byte pixels, RGB map/unmap, copy, fill, default alpha copy, and get-bits support.
- Unpacks `gx_color_index` into seven component bytes.
- Maintains a seven-word color cache for repeated 56-bit color patterns with endian-specific rotations.
- `mem_true56_fill_rectangle` optimizes repeated-byte grayscale fills, wide cached fills, and narrow widths.
- The wide fill path writes four 7-byte pixels as seven 32-bit words.
- `mem_true56_copy_mono` has explicit zero/one and stencil-only paths, writing seven bytes per selected pixel.
- `mem_true56_copy_color` delegates to `mem_copy_byte_rect`.
- Little-endian `mem_true56_word_device` swaps byte rectangles around fill, mono copy, and color copy operations.

Dependencies and notes:
- Debug statistic hooks match the neighboring high-bit-depth files.
- Uses `uint64_t` shifts for the high three component bytes.
