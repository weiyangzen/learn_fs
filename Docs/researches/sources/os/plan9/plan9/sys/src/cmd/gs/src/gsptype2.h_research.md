# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype2.h

Defines the client/internal interface for PatternType 2 shading patterns.

Key definitions:
- `gs_shading_t` forward declaration.
- `gs_pattern2_template_t`: pattern common fields plus `const gs_shading_t *Shading`.
- `gs_pattern2_instance_t`: pattern instance common fields, copied template, and `shfill` flag.
- GC descriptor macros for template and instance.
- Public device color type: `gx_dc_pattern2`, `gx_dc_type_pattern2`.

Exports:
- `gs_pattern2_init`
- `gx_dc_is_pattern2_color`
- `gx_dc_pattern2_fill_path`
- `gs_pattern2_set_shfill`
- `gx_dc_pattern2_shade_bbox_transform2fixed`
- `gx_dc_pattern2_get_bbox`
- `gx_dc_pattern2_can_overlap`
- `gx_dc_pattern2_has_background`

Integration:
- Includes `gspcolor.h`, `gsdcolor.h`, and `gxfixed.h`.
- Used by shading fill and pattern device-color handling.

Risk notes:
- Header notes that there is no `gs_cspace_build_Pattern2` helper even though it “should” exist.
