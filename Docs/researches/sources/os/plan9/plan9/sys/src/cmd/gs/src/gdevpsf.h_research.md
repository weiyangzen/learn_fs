# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsf.h

## Purpose
Declares the PostScript/PDF embedded font-writing interface used by Type 1, Type 2/CFF, CIDFont, CMap, TrueType, and stripped-font writers.

## Main Definitions
- `psf_glyph_enum_t`: stack-allocatable glyph enumeration state for list, range, bitmap, CID, and TrueType subset traversal.
- `psf_outline_glyphs_t`: collected outline-glyph subset state, including `.notdef` and optional subset data.
- `glyph_data_proc_t`: callback type for retrieving outline glyph data and the owning Type 1/Type 2 font.
- Write-option flags for Type 1, Type 2/CFF, TrueType, and CID font serialization.

## Key API
- Glyph enumeration:
  - `psf_enumerate_list_begin`,
  - `psf_enumerate_bits_begin`,
  - `psf_enumerate_glyphs_reset`,
  - `psf_enumerate_glyphs_next`.
- Subset helpers:
  - `psf_add_subset_pieces`,
  - `psf_sort_glyphs`,
  - `psf_sorted_glyphs_index_of`,
  - `psf_sorted_glyphs_include`.
- Outline glyph gathering:
  - `psf_check_outline_glyphs`,
  - `psf_get_outline_glyphs`,
  - Type 1-specific adapters from `gdevpsf1.c`.
- Font writers:
  - Type 1,
  - Type 2/CFF,
  - CIDFontType 0,
  - CMap,
  - TrueType/Type 42,
  - CIDFontType 2,
  - stripped TrueType/CID2,
  - Type 1 to Type 2 charstring conversion.

## Dependencies
Uses Ghostscript character code, glyph data, font, stream, CMap, Type 1, Type 42, and CID font types.

## Research Notes
This header is a cross-file contract. In this work item, only the Type 1 adapter/writer implementation is included; the Type 2, CMap, TrueType, CID, and conversion implementations are declared here but live in sibling files outside this group.
