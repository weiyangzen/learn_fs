# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtf.h

Font and CMap resource API/header for the `pdfwrite` text subsystem. It defines `pdf_font_resource_t`, encoding entries, standard-font bookkeeping, outline-font state, embedding status, and allocation/accessor routines.

Key contents:
- Documents the supported PDF font resource categories: Type 0 composite fonts, standard 14 fonts, Type 3 bitmap/vector fonts, Type 1/2, Type 42/TrueType, CIDFontType0, and CIDFontType2.
- Provides extensive documentation for PDF `BaseFont` naming rules by font type, including Type 0 descendant/CMap naming, TrueType space removal, Multiple Master non-embedded naming, and subset prefixes.
- Defines `pdf_char_glyph_pair_t` for character/glyph associations used in compatibility checks.
- Defines `pdf_font_write_contents_proc_t`, the callback used to write font-type-specific dictionary contents after generic font keys are written.
- Defines `pdf_encoding_element_t` for Encoding entries, including glyph, glyph-name string, and Differences marker.
- Defines `pdf_resource_ref_t` for resources referenced by Type 3 charprocs.
- Defines `pdf_font_resource_t` with common resource fields, FontType, write callback, BaseFont, descriptor/base-font links, width/used arrays, ToUnicode resource/CMap, and unions for Type 0, CIDFont, and simple font details.
- Type 0 data includes descendant font, Encoding name, CMapName, standard-CMap flag, and WMode.
- CIDFont data includes CIDSystemInfo object ID, CIDToGIDMap, glyphshow Type 0 font ID, vertical widths/origins, second used map, and parent Type 0 font pointer.
- Simple font data includes FirstChar/LastChar, BaseEncoding, Encoding, vertical origin array, and type-specific Type 1/TrueType/Type3 fields.
- Type 3 fields include FontBBox, FontMatrix, CharProcs, max Y offset, bitmap-font flag, used resource refs, and cached-bit map.
- Defines `pdf_font_embed_t` with standard/no/yes embedding statuses.
- Defines standard-font and outline-font bookkeeping structures and their GC descriptors.
- Declares allocation and cleanup for outline fonts, standard-font table access, font-cache freeing, Type 0/Type 3/standard/simple/CID font resource allocation, resource array resizing, font-resource font access, embedding-policy computation, BaseFont computation, document close hook, font-name selection, CMap allocation, and CID-to-GID map addition.

Notable dependencies:
- Includes `gdevpdtx.h` and references `gx_device_pdf`, `gs_font_type0`, `gs_cmap_t`, `pdf_base_font_t`, and `pdf_font_descriptor_t`.
- The header is consumed by most `gdevpdt*.c` files.

Research notes:
- The comments are central to understanding why font naming is delayed or recomputed at finish time.
- The structure intentionally keeps both PDF-visible widths and real PostScript widths because they can differ through Metrics/Metrics2/CDevProc.
- No filesystem behavior is present.
