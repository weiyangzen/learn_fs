# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevm24.c

Implements 24-bit RGB memory devices `image24` and little-endian `image24w`. Pixels are three bytes, with RGB mapping delegated to Ghostscript’s default RGB mapping procedures.

`mem_true24_fill_rectangle` is highly optimized. It has separate paths for wide fills, grayscale byte-identical colors, cached repeated RGB word patterns, narrow widths, and optional debug statistics. A per-device `color24` cache avoids recomputing rotated RGB word patterns.

`mem_true24_copy_mono` supports opaque halftone/inverted-mask cases and optimized stencil cases where only the one color is written. The stencil path processes first partial byte, full source bytes, and final residual bits.

`mem_true24_copy_alpha` blends a 2-bit or 4-bit alpha mask over existing RGB pixels by interpolating each channel toward the source color. `copy_color` delegates to byte-rectangle copying.

The word-oriented variant byte-swaps affected rectangles before/after calling the standard implementation or copying bytes. The file is a performance-sensitive true-color memory backend.
