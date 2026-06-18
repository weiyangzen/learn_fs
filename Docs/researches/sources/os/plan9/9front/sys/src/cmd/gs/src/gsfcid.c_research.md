# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsfcid.c

This file provides support routines and GC descriptors for CID-keyed fonts.

Implemented pieces:
- GC descriptors for CID system info and CIDFontType 0/1/2 font structures.
- GC descriptor for arrays of `gs_font_type1 *` used by CIDFontType 0 `FDArray`.
- `cid_system_info_set_null` and `cid_system_info_is_null`.
- `gs_font_cid_system_info`, which returns CIDSystemInfo for CIDFontType 0, 1, or 2 fonts.
- `gs_is_CIDSystemInfo_compatible`, comparing Registry and Ordering strings.
- `gs_font_cid0_enumerate_glyph`, a simple default glyph enumerator for CIDFontType 0.
- `gs_cid0_indexed_font`, returning an `FDArray` font by index.
- `gs_cid0_has_type2`, checking whether any CIDFontType 0 subfont is Type 2/CFF.

The font enumerator iterates CIDs, requests glyph data through the font’s `glyph_data` callback, skips empty glyphs, and frees glyph data after finding a present glyph.
