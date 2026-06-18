# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtb.c

## Purpose
Implements `pdf_base_font_t`, the stable copied-font layer used by PDF font resources and descriptors. It handles font copying, subset decisions, subset prefixes, glyph copying, embedded font writing, CharSet, and CIDSet output.

## Main Structures
- `pdf_base_font_t` stores:
  - Partial copied font and optional complete copied font.
  - Subsetting decision state: unknown/no/yes.
  - Standard-font flag.
  - Glyph/CID count and CIDSet bitmap.
  - Stable font name without subset prefix.
  - Written flag and FontFile Cos object pointer.

## Main Functions
- `pdf_base_font_alloc` copies the source font, strips existing subset prefixes, decides mandatory/possible subsetting by font type, allocates CIDSet for CID fonts, and stores a stable font name.
- `pdf_has_subset_prefix` validates `XXXXXX+` prefixes.
- `pdf_add_subset_prefix` hashes the used-glyph bitmap to synthesize a deterministic six-letter subset prefix.
- `pdf_base_font_copy_glyph` copies glyphs into the stable copy and marks CIDSet entries.
- `pdf_do_subset_font` lazily decides optional subsetting from `SubsetFonts` and `MaxSubsetPct`.
- `pdf_write_embedded_font` writes Type 1, Type1C/CFF, TrueType, CIDFontType0C, or CIDFontType2 embedded font streams.
- `pdf_write_CharSet` emits Type 1 subset CharSet.
- `pdf_write_CIDSet` emits the CIDSet stream for subset CID fonts.
- Accessors expose base font name, copied font, subset state, standard state, and FontFile object.

## Integration
- Used by `gdevpdtd.c` for descriptors and by `gdevpdtf.c` for font-resource naming/allocation.
- Uses Ghostscript font-copy APIs (`gs_copy_font`, `gs_copy_font_complete`, `gs_copy_glyph_options`) and PostScript font writers from `gdevpsf.h`.
- Writes data streams through `pdf_begin_data_stream`, `pdf_close_aside`, and Cos dictionaries.

## Risks and Notes
- Contains compatibility workarounds for Acrobat Reader 3/4/5 and Type 42 FontMatrix translation behavior.
- `pdf_add_subset_prefix` reads `used` in ushort-sized chunks, which assumes the used bitmap buffer is valid for the count.
- Type 2 conversion for `ft_encrypted2` without CFF support returns `gs_error_unregistered`.
- `pdf_base_font_alloc` frees only the top-level base font on some failure paths; copied-font ownership is expected to be managed by the Ghostscript memory model.
