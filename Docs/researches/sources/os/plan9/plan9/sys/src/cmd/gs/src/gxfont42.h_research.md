# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfont42.h

## Purpose
Defines Ghostscript Type 42 / TrueType font data structures and procedure declarations.

## Main Types
- `gs_type42_mtx_t`: metrics table descriptor with count, offset, and length.
- `gs_type42_data`: TrueType access callbacks, outline/metric procedures, cached table offsets, unitsPerEm, loca format, metrics tables, glyph counts, glyph lengths, glyph cache, and warning flags.
- `gs_font_type42`: `gs_font_base_common` plus `gs_type42_data`.

## Key Callbacks
- `string_proc`: retrieves bytes from the TrueType data source.
- `get_glyph_index`: maps Ghostscript glyph to TrueType GID.
- `get_outline`: retrieves glyph outline bytes.
- `get_metrics`: retrieves glyph metrics for WMode.

## Declared Procedures
- `gs_type42_font_init`
- `gs_type42_append`
- `gs_type42_get_metrics`
- `gs_type42_wmode_metrics`
- `gs_type42_default_get_metrics`
- `gs_type42_get_outline_from_TT_file`
- `gs_type42_enumerate_glyph`
- `gs_type42_glyph_info`
- `gs_type42_glyph_outline`
- `gs_type42_glyph_info_by_gid`

## Integration With Font Copying
`gxfcopy.c` creates copied Type 42 fonts by storing stripped TrueType data, overriding callbacks, copying selected glyph outlines, and filling fake hmtx/vmtx data.
