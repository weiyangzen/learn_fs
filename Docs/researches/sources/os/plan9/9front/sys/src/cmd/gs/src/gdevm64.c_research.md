# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevm64.c

Implements the 64-bit `image64` true-color memory device and little-endian `image64w` variant.

Key behavior:
- Registers `mem_true64_device` with 8-byte pixels, RGB map/unmap, copy, fill, default alpha copy, and get-bits support.
- Uses two 32-bit words per pixel; `PIXEL_SIZE` is defined as `2` in 32-bit-word units, while byte offset is `x << 3`.
- `declare_unpack_color` produces two 32-bit words, with explicit byte rearrangement on little-endian hosts.
- `mem_true64_fill_rectangle` writes repeated two-word pixels, with paths for wide and narrow fills.
- `mem_true64_copy_mono` handles explicit zero/one colors and the common transparent-zero stencil case.
- `mem_true64_copy_color` delegates to `mem_copy_byte_rect`.
- Little-endian `mem_true64_word_device` swaps byte rectangles around fill, mono copy, and color copy operations.

Dependencies and notes:
- The standard device’s byte offsets are correct through `x_to_byte(x) = x << 3`.
- In the word variant, `mem64_word_copy_color` uses `PIXEL_SIZE` in byte-pointer arithmetic even though `PIXEL_SIZE` is 32-bit-word count in this file; this is a notable sharp edge if maintaining this code.
