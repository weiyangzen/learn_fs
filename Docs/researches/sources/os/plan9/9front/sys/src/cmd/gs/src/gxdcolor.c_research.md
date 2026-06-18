# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxdcolor.c

This file implements the standard Ghostscript device color types for "none", "null", and "pure" colors and provides shared helpers for device color equality, phase, masked filling, black/white pixel caching, RasterOp no-source setup, and command-list serialization of device color indices.

The top of the file defines `gx_dc_type_data_none`, `gx_dc_type_data_null`, and `gx_dc_type_data_pure` as `gx_device_color_type_t` method vectors. The "none" type mostly returns errors or no-op results for invalid/unset colors; the "null" type consumes drawing operations without output; the "pure" type represents one encoded device pixel and delegates drawing to `fill_rectangle`, `copy_mono`, or `strip_copy_rop` depending on logical operation and mask/source requirements.

`gx_device_black`, `gx_device_white`, and `gx_device_decache_colors` maintain cached encoded black/white pixel values in `dev->cached_colors`. They use the device color mapping procedures (`get_color_mapping_procs`, `map_gray`, `encode_color`) and reset to `gx_no_color_index` when invalidated.

`gx_set_rop_no_source` builds an appropriate `gx_rop_source_t` for RasterOp operations with no source. It special-cases devices whose black pixel is 0 or 1 using static source records, otherwise it patches a caller-provided source with the encoded black pixel.

Device color type serialization support is handled by a private table mapping method-vector pointers to stable indices for command lists: none, null, pure, binary halftone, colored halftone, and WTS. `gx_get_dc_type_index` and `gx_get_dc_type_from_index` bridge between in-process pointers and command-list codes.

The pure color implementation serializes only the encoded pixel via `gx_dc_write_color` unless a saved device color already matches. `gx_dc_read_color` reconstructs encoded pixels, including the sentinel encoding for `gx_no_color_index` as a single `0xff` byte. The serialization byte width is based on `dev->color_info.depth`.

`gx_complete_halftone` initializes a colored halftone device color by setting its type, halftone pointer, component count, alpha, and active plane mask. `gx_dc_default_fill_masked` is the generic mask renderer: it scans mask rows using bit-run lookup tables and emits one-pixel-high rectangle fills for runs of active bits.

Filesystem relevance: none directly. It is central to Ghostscript's raster drawing path but does not interact with Plan 9 file, block, or VFS interfaces.
