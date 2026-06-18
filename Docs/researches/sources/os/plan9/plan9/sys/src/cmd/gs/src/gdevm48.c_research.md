# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm48.c

Implements 48-bit memory devices `image48` and little-endian `image48w`. Pixels are six bytes.

The fill path uses a three-word rotated color cache (`abcd`, `cdef`, `efab`) and has separate handling for gray byte-identical colors, wide non-gray fills, and narrow widths. The stride allows efficient two-pixel repeated stores.

`mem_true48_copy_mono` mirrors the other high-depth devices: unpack zero/one colors, process source bitmap bits, and optimize stencil cases by skipping zero source spans.

`mem_true48_copy_color` delegates to `mem_copy_byte_rect`; `image48w` wraps operations in byte swapping and direct byte rectangle copies.

This is a high-precision RGB memory backend with no custom alpha blending beyond default copy-alpha setup.
