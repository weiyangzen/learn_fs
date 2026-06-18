# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar42.c

Implements Type 42 / TrueType character display and cache setup.

Key behavior:
- `zchar42_set_cache` obtains metrics from PostScript `Metrics` when available, otherwise from TrueType glyph metrics via `gs_type42_wmode_metrics`.
- Handles vertical writing mode, including fallback vertical metrics for CID TrueType fonts derived from FontBBox.
- `.type42execchar` validates TrueType/CID TrueType show context, sets stroke width for stroked fonts, handles procedure glyph definitions, establishes current point, and calls cache setup.
- `type42_finish` appends the TrueType glyph outline to the current path with `gs_type42_append`, then fills or strokes.
- Fill path temporarily sets `fill_adjust` to `-1,-1`; stroke path uses `gs_stroke`.

Dependencies and coupling:
- Shares cache setup with `zcharout.c` and show context with `zchar.c`.
- Exports `zchar42_set_cache` for CID CDevProc handling in `zchar.c`.
