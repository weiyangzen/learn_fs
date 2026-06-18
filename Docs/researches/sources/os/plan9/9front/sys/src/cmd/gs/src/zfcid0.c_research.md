# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfcid0.c

Implements CIDFontType 0 / FontType 9 construction and glyph access.

Key behavior:
- Reads CID glyph data from `GlyphDirectory`, in-memory `GlyphData`, string arrays, or seekable `DataSource` streams.
- `z9_glyph_data` maps CIDs to FDArray index and CharString data through either GlyphDirectory records or CIDMap/GlyphData offsets.
- `z9_glyph_outline` renders CIDFontType 0 glyph outlines by selecting the appropriate descendant Type 1/Type 2 font and calling charstring outline code.
- `fd_array_element` builds descendant FDArray fonts, parsing Type 1 or Type 2 charstring parameters and replacing direct glyph accessors with invalidfont stubs.
- `.buildfont9` validates CID font dictionaries, builds FDArray descendants, creates the top-level CID font, stores GlyphDirectory/GlyphData/DataSource refs, and registers cleanup notification.
- `.type9mapcid` maps a CID to `<charstring> <font_index>`, falling back to CID 0 when glyph loading fails.

Dependencies:
- Uses CID data helpers from `zfcid.c`, Type 1/Type 2 font parameter parsing, font builders, streams, glyph-data lifetime helpers, and charstring outline functions.

Research notes:
- Important edge cases include missing glyphs, invalid FD indexes, GlyphData spanning multiple strings, stream I/O failures, and descendant parent-pointer cleanup.
