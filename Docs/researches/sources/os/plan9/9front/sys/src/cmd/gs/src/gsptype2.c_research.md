# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype2.c

Implements PatternType 2 shading patterns.

Main behavior:
- Defines PatternType 2 template/instance GC descriptors and type dispatch table.
- `gs_pattern2_init` initializes templates.
- `gs_pattern2_make_pattern` uses common pattern allocation, stores the shading template, and initializes `shfill` state.
- `gs_pattern2_set_shfill` marks instances used by `shfill`.
- `gs_pattern2_remap_color` creates a PatternType 2 device color without concrete color mapping.
- `gs_pattern2_set_color` updates overprint using the shading color space while temporarily disabling overprint mode.
- `gx_dc_pattern2_fill_path` and rectangle fill path render through `gs_shading_fill_path_adjusted`.
- Provides equality, halftone lookup, save-device-color support, bbox transform/get helpers, overlap detection for shading types 3/6/7, and background detection.

PatternType 2 colors are not cache-loaded like Type 1; load is a no-op and drawing delegates to the shading renderer.
