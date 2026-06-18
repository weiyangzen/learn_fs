# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtb.h

## Purpose
Defines the base-font interface for `pdfwrite`.

## Model
- A `pdf_base_font_t` is a stable copy of a supported Ghostscript base font.
- Supported font types are Type 1/2, TrueType/Type 42, CIDFontType 0, and CIDFontType 2.
- The module copies fixed font data at creation and copies glyphs as they are used.
- Optional complete copies allow the end-of-document writer to choose full embedding versus subsetting.
- Font names are stored without `XXXXXX+`; subset prefixes are added later if needed.

## API Surface
- Allocation and glyph-copying:
  - `pdf_base_font_alloc`
  - `pdf_base_font_copy_glyph`
- Name/font accessors:
  - `pdf_base_font_name`
  - `pdf_base_font_font`
  - `pdf_base_font_is_subset`
  - `pdf_base_font_drop_complete`
- Subset helpers:
  - `pdf_has_subset_prefix`
  - `pdf_add_subset_prefix`
  - `pdf_do_subset_font`
- Output helpers:
  - `pdf_write_FontFile_entry`
  - `pdf_write_embedded_font`
  - `pdf_write_CharSet`
  - `pdf_write_CIDSet`
- Standard/FontFile helpers:
  - `pdf_is_standard_font`
  - `pdf_set_FontFile_object`
  - `pdf_get_FontFile_object`

## Integration
- Included by font descriptor and font resource layers.
- Keeps PDF font naming and copied-font lifetime separate from font resource dictionaries.

## Risks and Notes
- The header documents name handling in detail because PDF font names are compatibility-sensitive.
- Clients must not add subset prefixes directly to the returned base-font name.
