# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcid2.c

## Role

`gsfcid2.c` creates CIDFontType 2 fonts from Type 42 fonts and wraps common TrueType cmap format 4 tables as Ghostscript CMaps.

## CIDFontType 2 Creation

`gs_font_cid2_from_type42` allocates `gs_font_cid2`, copies the Type 42 base, resets resource/list state, assigns a new id, sets `FontType` to CID TrueType, initializes null CIDSystemInfo, sets `CIDCount` from TrueType glyph count, and uses an identity CIDMap proc.

## TrueType CMap Wrapper

Defines `gs_cmap_tt_16bit_format4_t`, a subclass of `gs_cmap_t` referencing a Type 42 font and offsets into a Platform 3 / Encoding 1 / Format 4 cmap.

The decode proc reads two-byte character codes, linearly scans segments, applies `idDelta`/`idRangeOffset`, and returns CID glyphs. Enumeration procs expose one two-byte code range and lookup entries derived from TrueType segments.

`gs_cmap_from_type42_cmap` locates a suitable cmap subtable, allocates a Ghostscript CMap with dummy `none` CIDSystemInfo, and records segment-table offsets.

## Dependencies

Uses Type 42 font accessors, CMap internals, CID helpers, big-endian integer helpers, memory, and errors.

## Risks

The format 4 segment search is linear. The code targets only Platform 3 / Encoding 1 / Format 4; other Unicode cmap variants are rejected as invalid font for this wrapper.
