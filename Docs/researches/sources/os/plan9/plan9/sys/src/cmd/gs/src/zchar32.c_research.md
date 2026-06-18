# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zchar32.c

Implements Type 32 bitmap CID font glyph support.

Key behavior:
- `.makeglyph32` encodes bitmap glyph metrics into compact glyph strings. It supports 6-value WMode 0 metrics or 10-value dual-WMode metrics.
- Uses a short 5-byte metrics form when dimensions and offsets fit byte-sized constraints; otherwise uses 14- or 22-byte long forms.
- Validates bitmap size against calculated raster and bounding box dimensions.
- `.getmetrics32` decodes short and long forms, pushing width, height, metrics values, and consumed metrics-string size.
- `.removeglyphs` purges cached glyphs for a CID range in a Type 32 bitmap font.

Dependencies and coupling:
- Uses `gx_purge_selected_cached_chars` to invalidate font cache entries.
- Assumes CID bitmap fonts and 16-bit CID inputs.
- Metrics encoding is private to Type 32 font machinery.
