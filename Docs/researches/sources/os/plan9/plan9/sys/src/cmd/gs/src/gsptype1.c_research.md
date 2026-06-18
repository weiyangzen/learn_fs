# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsptype1.c

Implements PatternType 1 tiling patterns, including pattern instance creation, bitmap/pixmap pattern helpers, device color types, and pattern cache lookup.

Key areas:
- Pattern type vtable: `gs_pattern1_type` with base-space, make, get, remap, and set-color procedures.
- `gs_cspace_build_Pattern1`: builds Pattern color space with optional base color space.
- `gs_pattern1_init`, `gs_makepattern`, `gs_pattern1_make_pattern`.
- `compute_inst_matrix`, `clamp_pattern_bbox`: compute step matrix, device bbox, tile size, and clamp huge pattern bboxes to page intersection.
- `gs_pattern1_set_color`: updates overprint behavior for colored vs uncolored patterns.
- `gs_getpattern`: returns Type 1 template from client color.
- Bitmap/pixmap pattern support:
  - bitmap structure descriptors
  - `pixmap_info`
  - `free_pixmap_pattern`
  - `mask_PaintProc`, `image_PaintProc`, `bitmap_paint`
  - `gs_makepixmappattern`
  - `gs_makebitmappattern_xform`
- Device color types:
  - `gx_dc_pattern`
  - `gx_dc_pure_masked`
  - `gx_dc_binary_masked`
  - `gx_dc_colored_masked`
- Pattern cache:
  - `gx_pattern_cache_lookup`
  - load procs for colored and masked patterns.
- Save/equality/nonzero-components/write/read support for device colors.

Integration:
- Depends on generic pattern support in `gspcolor.c`, overprint parameters in `gsovrc.h`, image machinery, color spaces, device color vtables, and pattern cache internals.
- Fill rectangle procedures are declared here but implemented via `gxp1fill.h` inclusion pattern elsewhere.
- Exported device color type is referenced by other pattern/color modules.

Risk notes:
- `gs_cspace_build_Pattern1` checks `gs_color_space_num_components(pcspace)` before `pcspace` is allocated; source context suggests this likely meant `pbase_cspace`.
- Pattern scaling has compatibility switches and Adobe/traditional adjustments, making rendering sensitive to small numeric changes.
- Command-list serialization of patterns intentionally returns `unknownerror`; vector devices get only minimal save support.
- Bitmap/pixmap pattern helpers do not own original bitmap data; client lifetime must exceed pattern use.
