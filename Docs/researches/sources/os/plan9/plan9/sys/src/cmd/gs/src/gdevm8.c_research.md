# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm8.c

Implements 8-bit mapped-color memory devices `image8` and little-endian `image8w`. Each pixel is one byte.

`mem_mapped8_fill_rectangle` uses `bytes_fill_rectangle`. `mem_mapped8_copy_mono` dispatches to three helper loops for opaque (`mapped8_copy01`), stencil (`mapped8_copyN1`), and reverse-stencil (`mapped8_copy0N`) cases.

`mem_mapped8_copy_color` delegates to `mem_copy_byte_rect`. The strip-copy-rop implementation aliases `mem_gray8_rgb24_strip_copy_rop`.

The word-oriented device wraps fill and mono/color copies with `mem_swap_byte_rect` on little-endian systems, then uses either byte filling or the standard mapped8 copy routine.

This is the straightforward byte-per-pixel mapped memory backend and acts as a common grayscale/palette target.
