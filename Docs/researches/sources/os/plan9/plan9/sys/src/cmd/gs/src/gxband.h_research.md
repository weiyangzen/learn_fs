# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxband.h

Purpose: Defines band-list rendering parameters and saved-page bookkeeping for Ghostscript band processing.

Key definitions:
- `gx_band_params_t` stores transparency usage and optional band width, height, and buffer space.
- `gx_colors_used_t` tracks ORed color usage and slow raster-op usage per band group.
- `PAGE_INFO_NUM_COLORS_USED` is fixed at 50.
- `gx_band_page_info_t` stores command/block file names and handles, tile cache size, block file end position, actual band parameters, scan-line grouping for color use, and color-use entries.
- Convenience macros expose common `page_info` fields.

Behavior:
- Color-use precision is reduced when pages have more bands than 50 tracking entries.
- `PAGE_INFO_NULL_VALUES` provides initializer defaults.

Dependencies:
- Includes `gxclio.h` for command-list file pointer types and platform file-name sizes.

Notable risks:
- Fixed-size color-use array trades precision for bounded page-info size.
