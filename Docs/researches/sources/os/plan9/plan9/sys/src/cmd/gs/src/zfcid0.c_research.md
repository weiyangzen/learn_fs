# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfcid0.c

Implements CIDFontType 0 / Ghostscript FontType 9 operators.

Glyph access:
- `get_index()` parses multi-byte big-endian indexes from glyph data.
- `cid0_read_bytes()` reads glyph bytes from in-memory `GlyphData`, arrays of strings, or `DataSource` streams.
- `z9_glyph_data()` maps a CID glyph to descendant FDArray index and charstring bytes, using either `GlyphDirectory` or binary CIDMap/GlyphData.
- `z9_glyph_outline()` renders outlines through `zcharstring_outline()` using the selected descendant Type 1/Type 2 font.
- `z9_glyph_info()` delegates to generic Type 1 glyph info.

FDArray handling:
- `fd_array_element()` builds descendant Type 1 or Type 2 fonts from FDArray dictionaries, initializes charstring data, installs Type 1/Type 2 build procedures, and replaces direct glyph accessors with invalid-font stubs because outlines are supplied externally by the parent CID font.
- `notify_remove_font_type9()` clears descendant parent pointers when the parent type 9 font is finalized.

`.buildfont9` parses CID font dictionaries, validates `FDArray`, `CIDFontName`, `FDBytes`, `GlyphData`/`DataSource`, `CIDMapOffset`, and `GlyphDirectory`, builds all descendant fonts, builds the parent `gs_font_cid0`, installs glyph procedures, stores CID data refs in font data, defines the font, and links descendants back to the parent.

`.type9mapcid` maps a CID to a charstring and FDArray index. If glyph lookup fails, it falls back to CID 0 and reports invalid font if that also fails.

Registered in `zfcid0_op_defs`.
