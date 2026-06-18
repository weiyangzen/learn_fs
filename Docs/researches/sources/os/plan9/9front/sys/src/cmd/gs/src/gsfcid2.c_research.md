# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcid2.c

This file adapts Type 42 TrueType fonts into CIDFontType 2 fonts and builds a CMap from a common TrueType cmap table.

CIDFont creation:
- `gs_font_cid2_from_type42` allocates `gs_font_cid2`, copies the Type 42 base, resets font links/resource status, assigns a new ID, sets `FontType` to `ft_CID_TrueType`, initializes null CIDSystemInfo, sets `CIDCount` from `numGlyphs`, and installs identity `CIDMap_proc`.

TrueType cmap support:
- Defines `gs_cmap_tt_16bit_format4_t`, a CMap subclass for Platform 3, Encoding 1, Format 4 cmap subtables.
- `tt_16bit_format4_decode_next` decodes two-byte character codes by linearly scanning segments and applying `idDelta`/`idRangeOffset`.
- Range and lookup enumerators expose a single two-byte code range and derived mapping entries.
- `gs_cmap_from_type42_cmap` finds the desired cmap subtable, validates format 4, allocates the CMap, stores offsets to end/start/delta/range tables, and marks it as Unicode-derived.

The implementation prioritizes simplicity over speed; segment lookup is linear.
