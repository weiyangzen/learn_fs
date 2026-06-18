# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zchar32.c

This file implements Type 32 bitmap CID font glyph operators.

Key behavior:
- `.makeglyph32` serializes bitmap glyph metrics into compact short or long string forms.
- Validates metric arrays of either 6 values or 10 values, bitmap dimensions, CID range, Type 32 font type, and output string capacity.
- `.getmetrics32` decodes Type 32 metric strings and returns width, height, metrics, and consumed byte count.
- `.removeglyphs` purges cached glyphs in a CID range for a Type 32 bitmap font.

Important dependencies:
- Uses font cache APIs from `gxfcache.h`.
- Uses CID glyph code ranges via `gs_min_cid_glyph`.
- Requires `ft_CID_bitmap` fonts.

Registered operators:
- `.getmetrics32`
- `.makeglyph32`
- `.removeglyphs`
