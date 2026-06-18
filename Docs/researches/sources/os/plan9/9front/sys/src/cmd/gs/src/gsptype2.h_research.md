# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype2.h

Defines the client interface for PatternType 2 shading patterns.

Key structures:
- `gs_pattern2_template_t`: common pattern fields plus `const gs_shading_t *Shading`.
- `gs_pattern2_instance_t`: common instance fields, embedded template, and `shfill` flag.

Exports:
- `gx_dc_pattern2`
- `gs_pattern2_init`
- `gx_dc_is_pattern2_color`
- `gx_dc_pattern2_fill_path`
- `gs_pattern2_set_shfill`
- `gx_dc_pattern2_shade_bbox_transform2fixed`
- `gx_dc_pattern2_get_bbox`
- `gx_dc_pattern2_can_overlap`
- `gx_dc_pattern2_has_background`

The header notes that a PatternType 2 color-space builder is not provided.
