# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsf2.c

This file writes embedded CFF fonts containing either Type 1 or Type 2 charstrings, including ordinary Type 1/Type 2 fonts and CIDFontType 0 fonts. It is part of Ghostscript's PostScript/PDF font-output layer, not a filesystem implementation, but it uses Ghostscript streams as a binary serialization layer.

The central state is `cff_writer_t`, which carries output options, target stream, source base font, glyph-data callback, active CFF offset size, string tables, and font bounding box. `cff_string_table_t` implements a small open-addressed string table used to map CFF strings to SIDs, first checking the standard CFF string set and then entering private strings.

Important functionality:
- Encodes CFF integer, real, boolean, operator, offset, INDEX, string, and charstring structures.
- Converts Type 1 charstrings to Type 2 when `WRITE_TYPE2_CHARSTRINGS` is requested, otherwise copies encrypted or decrypted charstrings depending on `lenIV` options.
- Writes Top DICT variants for simple fonts, CIDFonts, and FDArray entries.
- Writes Private DICTs, local/global Subrs, Encoding, charset, CID charset, FDSelect, and CharStrings INDEX data.
- Uses `psf_get_type1_glyphs`, `psf_check_outline_glyphs`, and glyph enumerators from sibling utility code to validate and order subsets.
- For simple fonts, glyph ordering is normalized to `.notdef`, encoded glyphs, then unencoded glyphs.
- For CIDFontType 0, `cid0_glyph_data` dispatches CID glyph data through `FDArray` and records the correct subfont for FDSelect.

A major design point is offset convergence. CFF offsets and DICT sizes depend on each other because integer encodings are variable length. The writer first emits to a position-only stream with deliberately large placeholder offsets, recomputes sizes, loops until offsets stabilize, then writes the same content to the actual stream.

Notable constraints and risks:
- Several fixed-size tables are used, especially for CID string items and FD arrays; overflow returns Ghostscript errors such as `limitcheck` or `rangecheck`.
- The code mutates Type 1 private width fields when writing Type 2 charstrings to normalize widths.
- Comments note incomplete behavior: all Subrs are written even for subsets, with a note to optimize later.
- I/O failure is detected via `check_ioerror` on streams, but many helper writes are void-style stream emissions and rely on final checks.
