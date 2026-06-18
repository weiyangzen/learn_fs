# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfont32.c

## Purpose
Builds Type 32 bitmap CID fonts.

## Key Functions
- `zfont_no_encode_char()` returns `gs_no_glyph`; Type 32 encode-char should not be called.
- `zbuildfont32()` builds a bitmap CID font using `%Type32BuildGlyph`.

## Important Behavior
- `BuildChar` is absent; only `BuildGlyph` is supplied.
- Bitmap width/size behavior is set to always transform cached bitmaps.
- The font's `encode_char` procedure is replaced with a no-glyph stub.

## Research Notes
Compact builder for Ghostscript's bitmap CID font type.
