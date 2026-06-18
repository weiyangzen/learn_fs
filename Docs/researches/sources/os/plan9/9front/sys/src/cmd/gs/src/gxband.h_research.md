# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxband.h

Defines banding and saved-page metadata structures for Ghostscript band-list rendering.

Key definitions:
- `gx_band_params_t` carries transparency usage and optional band width, height, and buffer-space parameters.
- `gx_colors_used_t` summarizes colors seen in a band range, including an aggregate OR value and a slow-RasterOp flag.
- `gx_band_page_info_t` records command/block file names and handles, tile-cache size, block-file end position, actual band parameters, color-summary granularity, and a fixed-size color-use array.
- `PAGE_INFO_NUM_COLORS_USED` is fixed at 50 to bound page-info size while allowing reduced precision for many bands.
- Provides null initializer values and shorthand member aliases for conventional embedding.

Dependencies:
- Includes `gxclio.h` for command-list file pointer and file-name sizing definitions.
