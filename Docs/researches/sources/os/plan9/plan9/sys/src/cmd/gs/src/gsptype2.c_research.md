# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype2.c

Implements PatternType 2 shading patterns.

Key functions and objects:
- GC descriptors for Type 2 template/instance.
- `gs_pattern2_type` vtable.
- `gs_pattern2_init`: initializes template.
- `gs_pattern2_make_pattern`: creates instance via generic pattern common helper and stores `Shading`.
- `gs_pattern2_get_pattern`.
- `gs_pattern2_set_shfill`: marks instance as direct `shfill`.
- Device color type `gx_dc_pattern2`.
- `gx_dc_is_pattern2_color`.
- `gx_dc_pattern2_get_dev_halftone`: returns halftone from saved state.
- `gx_dc_pattern2_load`: no-op.
- `gs_pattern2_remap_color`: sets device color as PatternType 2 without concrete mapping.
- `gs_pattern2_set_color`: updates overprint using shading color space while temporarily disabling overprint mode.
- `gx_dc_pattern2_fill_path` / fill rectangle: delegates to `gs_shading_fill_path_adjusted`.
- Equality/save helpers.
- BBox/overlap/background helpers: `gx_dc_pattern2_shade_bbox_transform2fixed`, `gx_dc_pattern2_get_bbox`, `gx_dc_pattern2_can_overlap`, `gx_dc_pattern2_has_background`.

Integration:
- Depends on shading (`gsshade.h`), generic pattern color, device color, graphics state, and path internals.
- Shares pattern command-list write/read stubs with Type 1 (`gx_dc_pattern_write`, `gx_dc_pattern_read`).

Risk notes:
- PatternType 2 does not use a base space; shading’s own color space controls color/overprint.
- Direct fill delegates to shading code and uses saved imager state from pattern creation time.
- Self-overlap detection is type-number based for shading types 3, 6, and 7.
