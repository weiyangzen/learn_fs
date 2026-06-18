# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtb.h

BaseFont structure/API header for the `pdfwrite` text subsystem. It describes stable font copies, glyph-copying, subsetting, embedded font writing, and subset metadata emission.

Key contents:
- Documents the `pdf_base_font_t` concept used by `gdevpdt*.[ch]`: a stable copy of a supported Ghostscript base font with glyphs copied as needed.
- Explains why the implementation may store both a partial copied font and a complete font copy until the final subsetting decision is known.
- Documents PDF font-name handling and the rule that base font names stored here must not include a `XXXXXX+` subset prefix.
- Declares allocation and accessors for base-font name and copied/complete font pointers.
- Declares subset tests, complete-font dropping, glyph-copying, subset-prefix detection/creation, subset decision, FontFile entry writing, embedded font writing, CharSet writing, CIDSet writing, standard-font testing, and FontFile object accessors.

Notable dependencies:
- Includes `gdevpdtx.h` for shared text/font subsystem types.
- Exposes `gs_font_base`, `gs_glyph`, `gs_matrix`, `gs_string`, `cos_dict_t`, and `gx_device_pdf` interactions indirectly through the subsystem.

Research notes:
- The header explicitly limits supported base font types to Type 1/2, TrueType/Type42, CIDFontType 0, and CIDFontType 2.
- It is a private subsystem API, but its comments are important design documentation for font copying and naming.
- No filesystem behavior is present.
