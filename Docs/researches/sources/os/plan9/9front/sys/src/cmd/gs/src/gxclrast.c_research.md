# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxclrast.c

Command-list interpreter and rasterizer for Ghostscript band playback.

Key behavior:
- Defines `clist_playback_band`, the main interpreter loop for command-list stream opcodes.
- Maintains a refilled command buffer, current clist drawing state, tile state/cache entries, path state, clipping path, imager state, current device color, image state, halftone buffer, and optional compositor target device.
- Decodes command families for misc state, colors and delta colors, rectangles, tile/copy bitmap operations, extended graphics state, image setup/data, serialized params, compositors, serialized halftones, drawing colors, path segments, and path painting.
- Dispatches decoded drawing operations to target device procs such as `fill_rectangle`, `strip_tile_rectangle`, `copy_mono`, `copy_color`, `copy_alpha`, `fill_mask`, `strip_copy_rop`, `begin_typed_image`, `gx_fill_path_only`, and `gx_stroke_path_only`.
- Handles compressed bitmap/tile payloads using RunLength and CCITTFax decode helpers; unpacks short rasters into aligned buffers.
- Reconstructs compact path segment encodings through `clist_decode_segment`, including relative lines, compact curves, closepath, and polyfill shapes.
- Reads serialized color spaces, including temporary DeviceGray/RGB/CMYK and Indexed spaces with table or proc-backed lookup maps.
- Reads `put_params` command payloads into a `gs_c_param_list` and applies them to the clist reader device.
- Reads compositor commands by looking up compositor IDs, deserializing compositor payloads, creating compositor devices, and invoking clist read-update hooks.
- Reads serialized halftones in one or more segments and installs them with `gx_ht_read_and_install`.

Notable dependencies:
- Command encoding definitions and clist structures from `gxcldev.h`/`gxclpath.h`.
- Color-space, color-map, halftone, image, path, compositor, stream, and device-proc infrastructure.
- Compression helpers initialized in `gxclutil.c` and zlib/CCITT/RLE stream templates elsewhere.

Research notes:
- The file is the read-side counterpart to clist writing utilities and rectangle/path command emitters.
- Bad opcodes are treated as fatal and dump command-buffer context for debugging.
- Some behavior is intentionally limited: only DeviceGray/RGB/CMYK color-space indices are accepted in `read_set_color_space`; others return rangecheck/NYI.
- Alpha is routed through RGB-alpha mapping/copy-alpha paths, but CMYK remapping comments elsewhere note alpha is ignored for CMYK.
- The interpreter owns multiple temporary allocations and carefully frees indexed tables/maps, clip paths, paths, imager state, data buffers, halftone buffers, and compositor devices on exit.
