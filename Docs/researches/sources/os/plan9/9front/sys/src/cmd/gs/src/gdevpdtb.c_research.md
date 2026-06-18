# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpdtb.c

BaseFont implementation for `pdfwrite`. It makes stable copies of Ghostscript fonts, tracks glyph usage, decides subsetting, creates subset prefixes, and writes embedded font programs into PDF stream objects.

Key behavior:
- Defines `pdf_base_font_t`, holding copied and complete font copies, subset decision state, standard-font flag, glyph count, optional CIDSet bitmap, font name, written flag, and FontFile COS object.
- Recognizes subset prefixes of the form `XXXXXX+` and strips them when building stable font names.
- Builds deterministic subset prefixes by hashing the used-glyph bitmap and prepending six uppercase letters plus `+`.
- `pdf_base_font_alloc` copies fixed font data into stable memory, zeroes TrueType/Type42 FontMatrix translation components for viewer compatibility, decides initial subset policy, optionally creates a complete copy, counts Type 1 glyphs, allocates CIDSet for CID fonts, and stores a prefix-free font name.
- CID fonts and large TrueType fonts are forced toward subsetting; Type 1/2 and smaller TrueType fonts may remain complete depending on Distiller parameters.
- `pdf_base_font_copy_glyph` copies a used glyph into the saved font and marks the CIDSet bit when appropriate.
- `pdf_do_subset_font` finalizes the subset decision using `SubsetFonts` and `MaxSubsetPct`.
- `pdf_write_FontFile_entry` chooses `/FontFile`, `/FontFile2`, or `/FontFile3` depending on font type and `ResourcesBeforeUsage`.
- `pdf_adjust_font_name` appends a unique `~<id>` suffix for Acrobat Reader 3 compatibility when emitting unsubsetted embedded fonts in PDF 1.2.
- `pdf_write_embedded_font` writes Type 1, Type1C/CFF, TrueType, CIDFontType0C, and CIDFontType2 font programs using Ghostscript PostScript font writers and records stream dictionary lengths/subtypes.
- Writes Type 1 `/CharSet` strings for subsetted fonts and CID `/CIDSet` streams for subsetted CID fonts.
- Exposes helpers for standard-font status and storing/retrieving the associated FontFile COS object.

Notable dependencies:
- Uses Ghostscript font copy/writer APIs from `gxfcopy.h`, `gxfont42.h`, and `gdevpsf.h`.
- Uses PDF stream/object helpers from `gdevpdfx.h` and `gdevpdfo.h`.
- Interfaces with font resource and descriptor layers through `gdevpdtb.h` and `gdevpdtf.h`.

Research notes:
- The file documents Distiller-style subsetting policy and intentionally differs for Type 1, TrueType, and CID fonts.
- FontMatrix translation is cleared because older Adobe rasterizers/viewers mishandle Type42/TrueType matrix translations.
- TrueType embedding uses a position-only stream first to compute `/Length1`.
- Error paths in `pdf_base_font_alloc` free the `pdf_base_font_t` wrapper but rely on Ghostscript allocation ownership patterns for copied fonts.
- This is font/PDF output code, not filesystem code.
