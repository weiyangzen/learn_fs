# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtf.c

Font and CMap resource implementation for `pdfwrite` text. It defines PDF font resource GC behavior, standard-font recognition, embedding policy, BaseFont computation, allocation for Type 0/Type 3/simple/CID resources, CID width arrays, and CMap resource allocation.

Key behavior:
- Defines public/private GC descriptors for `pdf_font_resource_t`, encoding elements, standard-font bookkeeping, and outline-font bookkeeping.
- Enumerates and relocates different resource subfields depending on font type: Type 0 descendant fonts/CMap names, simple Encoding/v arrays, Type 3 charprocs/cached resources, and CID widths/maps/parent/used2 arrays.
- Defines the 14 standard PDF fonts, their names, and base encodings.
- Scans loaded font resources to find standard fonts by resource status, UniqueID, and standard names.
- Compares candidate font outlines with standard fonts to decide whether a font can be treated as a standard 14 font.
- Allocates `pdf_outline_fonts_t` and the per-device standard-font table.
- Implements generic font-resource allocation with width and used-bit arrays, plus encoded simple-font allocation with 256 Encoding entries and vertical-origin data.
- Resizes font resource arrays, especially for CID fonts whose documents use CIDs beyond the advertised CIDCount.
- Determines whether a font is symbolic, whether font names appear in AlwaysEmbed/NeverEmbed parameter arrays, and whether standard fonts should be embedded or treated as base 14.
- `pdf_font_embed_status` applies PDF/X, compatibility level, standard-font appearance, `EmbedAllFonts`, symbolic-font behavior, and embed lists to return `FONT_EMBED_STANDARD`, `FONT_EMBED_NO`, or `FONT_EMBED_YES`.
- `pdf_compute_BaseFont` computes PDF BaseFont names for simple, CID, and Type 0 fonts; removes spaces for TrueType names; handles Multiple Master non-embedded names; appends CMap names for Type 0 CID descendants; adds subset prefixes at finish time; and synchronizes descriptor FontName.
- Allocates Type 0 font resources with descendant fonts and CMap names.
- Allocates Type 3 font resources for synthesized bitmap/vector fonts.
- Allocates standard base-14 font resources and stores original standard font mappings.
- Allocates simple Type 1/TrueType font resources backed by FontDescriptors.
- Allocates CIDFont resources, including CIDToGIDMap for CIDFontType2, WMode-1 usage maps, and early CIDSystemInfo object writing.
- Lazily allocates CID horizontal/vertical width arrays and vertical origin arrays.
- `pdf_cmap_alloc` delegates CMap writing to `pdf_write_cmap`.

Notable dependencies:
- Uses font copying and standard-font comparison helpers from Ghostscript font internals (`gxfcache.h`, `gxfcid.h`, `gxfcmap.h`, `gxfcopy.h`, `gxfont1.h`).
- Uses descriptor/base-font APIs from `gdevpdtb.h` and `gdevpdtd.h`.
- Uses font-writing declarations from `gdevpdtw.h`.

Research notes:
- The code preserves Acrobat Distiller behavior differences between PDF 1.2 and 1.3 around base 14 font embedding.
- The standard-font path uses actual appearance/outlines, not just names, to avoid treating unrelated fonts with standard names as base 14 fonts.
- CID resource allocation writes CIDSystemInfo immediately to avoid depending on live font objects later.
- This is PDF font resource management, not filesystem code.
