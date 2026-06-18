# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar1.c

Implements Type 1 character display and shared CharString execution for Type 1, Type 2, disk-based, and CID Type 0 paths.

Key behavior:
- `.type1execchar` delegates to `charstring_execchar` with Type 1/disk font masks.
- `charstring_execchar` validates current show context, handles PostScript-procedure glyph definitions, initializes Type 1 interpretation, extracts metrics, and chooses FontBBox or no-FontBBox rendering paths.
- The bbox path sets cache device early using FontBBox and metrics; if the drawn path exceeds FontBBox, it enlarges FontBBox and retries.
- The no-bbox path builds the path first, derives bbox from the path, then sets cache device; anti-aliased rendering may rebuild the path after cache setup.
- Supports unknown `OtherSubrs` by moving Type 1 interpreter state to the heap, pushing saved arguments/procedures onto the estack, and resuming later.
- `zsetweightvector` sets multiple-master weight vectors for Type 1/2 fonts.
- Exposes `z1_data_procs` for glyph data, subr data, seac data, and Type 1 push/pop callbacks.
- `zchar1_glyph_outline`, `zcharstring_outline`, `z1_glyph_info`, and `z1_set_cache` provide outline, metrics, and cache services for higher-level font code.

Dependencies and coupling:
- Depends heavily on `gxtype1`, `gxfont1`, `ichar1`, and `icharout`.
- Shares cache setup through `zcharout.c`.
- Contains compatibility choices for fill rule, stroke width, FontBBox-as-Metrics2, and Adobe behavior around stroked fonts.
