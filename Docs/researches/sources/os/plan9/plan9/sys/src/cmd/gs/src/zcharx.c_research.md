# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zcharx.c

Implements Level 2 character operators `glyphshow`, `.glyphwidth`, `xshow`, `yshow`, and `xyshow`.

Key behavior:
- `glyph_show_setup` accepts integer CIDs for CID fonts and names for non-CID fonts, converting to a `gs_glyph`.
- `glyphshow` begins a glyph show enumerator and reuses the generic show continuation pipeline.
- `.glyphwidth` begins a glyph-width enumerator and finishes through `finish_stringwidth`.
- `moveshow` converts numeric arrays/strings into a temporary float array and calls `gs_xyshow_begin` with x and/or y displacements.
- Temporary movement arrays are freed on setup errors; successful ownership passes to the text enumerator path.

Dependencies and coupling:
- Level 2 operator table only.
- Reuses `op_show_enum_setup`, `op_show_finish_setup`, and `op_show_continue` from `zchar.c`.
- Uses binary number array helpers from `ibnum.h`.
