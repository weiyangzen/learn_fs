# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsf2.c

This file writes embedded Compact Font Format (CFF) fonts containing Type 1, Type 2, and CIDFontType 0 charstrings for Ghostscript's PostScript/PDF font-output path. It is not filesystem code; it serializes font resources to Ghostscript `stream` objects.

The central state is `cff_writer_t`, carrying output options, the target stream, source base font, glyph-data callback, active CFF offset width, standard/private string tables, and the font bounding box. `cff_string_table_t` implements a compact open-addressed SID table: lookups first try the standard CFF string set and then enter nonstandard strings into the private string INDEX.

Major responsibilities:
- Encode CFF primitive structures: integers, reals, booleans, operators, offsets, INDEXes, string SIDs, charstrings, and dict entries.
- Write Top DICT variants for simple Type 1/Type 2 fonts, CIDFontType 0 top dictionaries, and FDArray subfont dictionaries.
- Write Private DICT data including BlueValues, stem data, width defaults, lenIV policy, language group, expansion factor, and local Subrs offsets.
- Serialize CharStrings INDEX, local/global Subrs INDEXes, simple-font Encoding, simple charset, CID charset, FDSelect, and FDArray.
- Convert Type 1 charstrings to Type 2 through `psf_convert_type1_to_type2` when requested; otherwise copy encrypted/decrypted charstrings depending on `lenIV` and `WRITE_TYPE2_NO_LENIV`.
- Use `psf_get_type1_glyphs`, `psf_check_outline_glyphs`, and glyph enumerators from sibling utility code to validate and order subsets.

For simple fonts, `psf_write_type2_font` normalizes glyph ordering to `.notdef`, encoded glyphs, then unencoded glyphs. It explicitly stores Encoding and charset data rather than relying on predefined tables. For CIDFontType 0, `psf_write_cid0_font` enumerates selected CIDs, writes ROS information, builds FDSelect mappings from `cidata.glyph_data`, and uses each selected FDArray subfont as the Private DICT/Subrs owner for its glyphs.

A key design point is offset convergence. CFF offsets and DICT sizes depend on one another because integer encodings are variable length. Both public writers first emit to a position-only stream using large placeholder offsets, recompute section sizes, loop until offsets stabilize, and only then replay the same write to the real output stream.

Notable constraints and risks:
- Some fixed arrays are tight: CID FDArray/subrs arrays are capped at 256, CID string table storage is fixed, and simple-font string tables are sized from glyph count plus `MAX_CFF_MISC_STRINGS`.
- The code mutates Type 1 private width fields when emitting Type 2 charstrings, setting `defaultWidthX` and `nominalWidthX` to zero for non-`ft_encrypted2` sources.
- Subr subsetting is not implemented; comments state all Subrs are written even for subsets unless charstrings are converted and Subrs are expanded inline.
- Stream write helpers mostly rely on final `check_ioerror` calls rather than checking every byte emission.
