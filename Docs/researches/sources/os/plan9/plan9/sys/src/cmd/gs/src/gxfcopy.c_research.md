# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfcopy.c

## Purpose
Implements Ghostscript high-level output font copying and incremental glyph subsetting. It creates copied font objects that preserve enough structural, metric, subroutine, and glyph-outline data to query/render/write subsets for Type 1/2, Type 42 TrueType, CIDFontType 0, and CIDFontType 2 fonts.

## Main Concepts
- Defines `gs_copied_font_data_t`, attached through `gs_font.client_data`, as the central copied-font state.
- Stores copied glyph vector data in `gs_copied_glyph_t` arrays indexed by glyph name hash slot, CID, or TrueType GID depending on font type.
- Maintains optional glyph-name tables, extra-name lists, Type 1/2 Subrs/GlobalSubrs, TrueType stripped font data, Type 42 fake metrics, Type 1/2 encodings, and CID maps.
- Supplies copied-font procedure vectors so copied fonts can answer `font_info`, `encode_char`, `enumerate_glyph`, `glyph_info`, `glyph_outline`, `glyph_name`, and `build_char`.

## Public API Implemented
- `gs_copy_font`: copies the non-glyph font shell and initializes font-type-specific copied data.
- `gs_copy_glyph`: copies one glyph plus dependent subglyph pieces.
- `gs_copy_glyph_options`: copy with `COPY_GLYPH_NO_OLD`, `COPY_GLYPH_NO_NEW`, and `COPY_GLYPH_BY_INDEX`.
- `gs_copied_font_add_encoding`: adds encoding entries for copied Type 1/2/42 fonts.
- `gs_copy_font_complete`: copies all glyphs and relevant encoding entries.
- `gs_copied_can_copy_glyphs`: compatibility check for merging/copying glyphs between fonts.
- `copied_drop_extension_glyphs`: removes extension glyph aliases before embedded font output.

## Font-Type Paths
- Type 1/Type 2:
  - Copies local and global subroutines.
  - Uses hashed glyph-name slots.
  - Copies CharString bytes and names.
  - Implements copied Type 1 glyph data, subr data, `seac` lookup, and outline interpretation.
- Type 42:
  - Writes stripped TrueType/CID2 data into memory via `psf_write_truetype_stripped` or `psf_write_cid2_stripped`.
  - Stores glyph outlines separately and patches fake hmtx/vmtx metrics.
  - Uses GID-indexed glyph slots and name-to-GID mapping.
- CIDFontType 0:
  - Copies CIDSystemInfo and Type 1/2 FDArray subfonts.
  - Shares parent glyph storage/global subrs with copied subfonts.
  - Stores FD index bytes as a prefix before charstring data.
- CIDFontType 2:
  - Extends Type 42 copying with a copied `CIDMap`.
  - Maps CIDs to GIDs and supports copying by CID or by GID.

## Important Internal Routines
- `copy_string` / `uncopy_string`: explicit GC-managed string duplication/freeing.
- `copy_subrs`: scans then copies Type 1/2 Subrs or GlobalSubrs into packed data plus start offsets.
- `copied_glyph_slot`, `named_glyph_slot_hashed`, `named_glyph_slot_linear`: glyph lookup and insertion-slot resolution.
- `copy_glyph_data`: detects duplicate/conflicting glyph definitions and owns copied vector bytes.
- `copy_glyph_name`: fills primary and extra glyph-name tables.
- `compare_glyphs`: compares widths, composite pieces, and outline bytes for compatibility.
- `same_type1_hinting`, `same_type42_hinting`, `same_cid0_hinting`, `same_cid2_hinting`: hinting compatibility checks.

## Dependencies
Uses core Ghostscript font, glyph, Type 1, Type 42, CID, path, text, stream, memory, and PostScript font writer internals, including `gxfont.h`, `gxfont1.h`, `gxfont42.h`, `gxfcid.h`, `gxfcopy.h`, `gxfcache.h`, `gxtype1.h`, `gxtext.h`, `gzstate.h`, and `gdevpsf.h`.

## Notable Risks / Edge Cases
- Compatibility logic is subtle because it compares both font identity/hinting and subset glyph outlines.
- `compare_glyphs` contains a suspicious self-comparison: `memcmp(gdata0.bits.data, gdata0.bits.data, gdata0.bits.size)`, which cannot detect differences against `gdata1`.
- `expand_CIDMap` allocates a replacement map but does not visibly free the previous map before overwriting `cfdata->CIDMap`.
- `copied_drop_extension_glyphs` has suspicious pointer use in one separator comparison: it passes `name + j` rather than the glyph-name byte buffer.
- Copied fonts intentionally do not preserve all PostScript dictionary data such as Metrics arrays, CDevProc, OtherSubrs, and full FontInfo.
