# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfcid.c

## Role

`gsfcid.c` provides support routines and GC descriptors for CID-keyed fonts.

## GC/Descriptors

Defines structure descriptors for `CIDSystemInfo`, CID font data, CIDFontType 0, CIDFontType 1, CIDFontType 2, and FDArray pointer arrays. The enum/reloc procedures delegate to base font or CID data descriptors and handle FDArray/proc pointers.

## CIDSystemInfo Helpers

- `cid_system_info_set_null` clears Registry, Ordering, and Supplement.
- `cid_system_info_is_null` tests the null representation.
- `gs_font_cid_system_info` returns CIDSystemInfo for CID font types and null for non-CID fonts.
- `gs_is_CIDSystemInfo_compatible` compares Registry and Ordering but ignores Supplement.

## Font Helpers

`gs_font_cid0_enumerate_glyph` iterates CIDs, asks the CID font for glyph data, skips missing/empty glyphs, and returns available glyphs. It frees glyph data before returning.

`gs_cid0_indexed_font` returns a subfont from FDArray and prints an error if called on a non-CIDFontType 0 font.

`gs_cid0_has_type2` scans FDArray for Type 2 encrypted subfonts.

## Dependencies

Uses font/CID internals from `gxfcid.h`, base font descriptors, memory, matrix, and error helpers.

## Risks

`gs_cid0_indexed_font` does not bounds-check `fidx`. Callers must validate FDArray indexes. Compatibility ignores Supplement, which is intentional for many CMap/font matching cases but not full structural equality.
