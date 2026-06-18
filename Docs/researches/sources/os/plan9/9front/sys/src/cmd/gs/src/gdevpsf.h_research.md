# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsf.h

## Purpose
Declares the PostScript/PDF font-writing interface for embedded fonts, glyph enumeration, subset handling, Type 1/Type 2/CID/TrueType/CMap writers, and Type 1-to-Type 2 conversion.

## Main Declarations
- `psf_glyph_enum_t`: opaque-ish stack-allocatable glyph enumerator for full fonts or subsets.
- Glyph enumeration APIs:
  - list-based enumeration,
  - bit-vector subset enumeration,
  - reset and next functions.
- Subset helpers:
  - add composite glyph pieces,
  - sort and deduplicate glyph lists,
  - binary-search membership/index helpers.
- `psf_outline_glyphs_t`: selected outline glyph metadata for Type 1/Type 2/CIDFontType 0 writers.
- `glyph_data_proc_t`: callback for retrieving glyph outline data and source Type 1 font.

## Writer APIs
- Type 1:
  - `psf_type1_glyph_data`,
  - `psf_get_type1_glyphs`,
  - `psf_write_type1_font`.
- Type 2/CFF:
  - `psf_write_type2_font`,
  - `psf_write_cid0_font`.
- CMap:
  - `psf_write_cmap`.
- TrueType/CIDFontType 2:
  - `psf_write_truetype_font`,
  - stripped TrueType writer,
  - CIDFontType 2 writer,
  - stripped CIDFontType 2 writer.
- CharString conversion:
  - `psf_convert_type1_to_type2`.

## Research Notes
This header is the font embedding contract used by PostScript/PDF output code. The file in this group implementing part of it is `gdevpsf1.c`, focused on Type 1 font output.
