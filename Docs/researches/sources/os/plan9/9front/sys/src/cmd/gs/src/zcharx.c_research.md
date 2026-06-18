# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zcharx.c

This file implements Level 2 character operators beyond basic `show`.

Key behavior:
- `glyphshow` renders a glyph by name for simple fonts or by CID integer for CID fonts.
- `.glyphwidth` measures a glyph and returns width using the same text-enumerator flow as `stringwidth`.
- `xshow`, `yshow`, and `xyshow` accept a string plus numeric array/string and apply per-character displacement values.
- `moveshow` normalizes numeric arrays/strings into a temporary float array, starts `gs_xyshow_begin`, and frees the array on setup failure.

Important dependencies:
- Uses numeric packed-array helpers from `ibnum.h`.
- Reuses show setup and finishing helpers from `ichar.h`.
- Registered as Level 2 operators in `zcharx_op_defs`.

Research notes:
- The file depends on correct temporary allocation lifetime: the float displacement array is handed to the text enumerator on success.
