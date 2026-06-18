# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpdtf.h

## Purpose
Defines PDF font-resource and CMap-resource structures and APIs for `pdfwrite`.

## Main Definitions
- Defines `pdf_char_glyph_pair_t`, encoding elements, resource references, and font write callback type.
- Defines `pdf_font_resource_t`, a resource wrapper for:
  - Type 0 composite fonts.
  - CIDFontType 0 and CIDFontType 2 descendants.
  - Simple Type 1/2 and TrueType fonts.
  - Type 3 fonts, including bitmap/vector charprocs.
  - Standard 14 fonts.
- Stores BaseFont, FontDescriptor, Widths, used bitmaps, ToUnicode resources/CMaps, and variant-specific union data.
- Defines `pdf_font_embed_t` with standard/no/yes embedding states.
- Defines `pdf_standard_font_t` and `pdf_outline_fonts_t`.

## API Surface
- Outline/standard font lifecycle:
  - `pdf_outline_fonts_alloc`
  - `pdf_standard_fonts`
  - `pdf_clean_standard_fonts`
  - `pdf_free_font_cache`
- Resource allocation:
  - `pdf_font_type0_alloc`
  - `pdf_font_type3_alloc`
  - `pdf_font_std_alloc`
  - `pdf_font_simple_alloc`
  - `pdf_font_cidfont_alloc`
  - `font_resource_encoded_alloc`
- Resource utilities:
  - `pdf_resize_resource_arrays`
  - `pdf_font_resource_font`
  - `pdf_font_embed_status`
  - `pdf_compute_BaseFont`
  - `pdf_choose_font_name`
  - `pdf_obtain_cidfont_widths_arrays`
- CMap/CID utilities:
  - `pdf_cmap_alloc`
  - `pdf_font_add_cid_to_gid`

## Integration
- Central structural contract used by text processing, descriptor generation, base-font embedding, and font writing modules.
- Relies on `gdevpdtx.h` for core text/device abstractions.

## Risks and Notes
- The struct is large and variant-heavy; callers must only access union arms that match `FontType`.
- The header’s long BaseFont naming notes are important for PDF compatibility and subset correctness.
