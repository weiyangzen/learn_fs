# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtw.c

Font and CMap resource writer for pdfwrite text output. This is the serialization stage for PDF font dictionaries, widths, encodings, ToUnicode resources, CID metadata, CIDToGID maps, descriptors, and CMap streams.

Key behavior:
- Writes simple-font `/FirstChar`, `/LastChar`, and `/Widths` arrays with rounded PDF numbers.
- Detects whether an encoding element differs from the base encoding and finds the first differing character.
- Determines whether a simple font needs a ToUnicode CMap by checking glyph names against `gs_c_pdf_glyph_type[]` and masks from `gdevpdtv.h`.
- Writes Encoding dictionaries with `/BaseEncoding` and `/Differences`, including Type 3 compatibility behavior that forces differences for used chars.
- Writes encoding references either to a separate object or directly to a base encoding name.
- Writes Type 0 font dictionaries with `/Encoding`, `/DescendantFonts`, and `/Subtype/Type0`.
- Finishes Type 3 dictionaries by writing FontBBox, Widths, and `/Subtype/Type3`.
- Writes standard and simple Type 1/TrueType font dictionaries, including widths for non-standard simple fonts.
- Computes CIDFont default widths using a histogram over used glyph widths, then writes `/DW`, `/W`, `/DW2`, and `/W2` as needed.
- Writes CIDFontType0 and CIDFontType2 common dictionary content, including optional `/CIDSystemInfo`.
- For CIDFontType2, detects non-identity `/CIDToGIDMap`, emits a compressed binary stream, and writes two-byte GID entries.
- `pdf_write_font_resource` computes/writes ToUnicode resources when required, opens the font object, writes BaseFont, FontDescriptor, ToUnicode, Type/Name, global OPDFRead marker, and delegates to the per-font write procedure.
- `pdf_close_text_document` finalizes text resources in required order: clean standard fonts, free font cache, write CharProcs, finish descriptors and embedded fonts, write CIDFonts, write Fonts, write FontDescriptors, then bitmap font Encoding.
- Writes CIDSystemInfo dictionaries, encrypting Registry and Ordering strings when object encryption is active.
- `pdf_write_cmap` creates compressed CMap streams, fills COS dictionary metadata for non-ToUnicode CMaps, and delegates CMap body writing to `psf_write_cmap`.

Notable dependencies:
- Font/resource definitions from `gdevpdtf.h`, descriptor handling from `gdevpdtd.h`, bitmap-font Encoding from `gdevpdti.h`, generated glyph attributes from `gdevpdtv.h`.
- Uses `sarc4.h` for PDF string encryption in CIDSystemInfo.

Research notes:
- This file is tightly coupled to PDF compatibility rules and Acrobat historical behavior.
- It is not responsible for choosing font resources; it serializes resources already built by the text/font-resource layers.
