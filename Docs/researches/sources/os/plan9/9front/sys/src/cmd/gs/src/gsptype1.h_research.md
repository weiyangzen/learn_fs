# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsptype1.h

Defines the client interface for PatternType 1 tiling patterns.

Key structure:
- `gs_pattern1_template_t`, extending common pattern fields with `PaintType`, `TilingType`, `BBox`, `XStep`, `YStep`, and `PaintProc`.

Exports:
- `gs_cspace_build_Pattern1`
- `gs_pattern1_init`
- `gs_makepattern`
- `gs_getpattern`
- `gs_makepixmappattern`
- `gs_makebitmappattern_xform`
- Backward-compatible aliases/macros for older client pattern API.

Documents mask versus colored pixmap conventions, indexed-color requirements, white-index transparency handling, and raw image-data lifetime expectations.
