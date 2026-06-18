# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxtype1.c

Shared support for Ghostscript Type 1 and Type 2 charstring interpreters.

Key behavior:
- Defines GC descriptors for Type 1 font/state objects, including enumeration and relocation of active charstring/subroutine glyph data in the interpreter stack.
- `gs_type1_interp_init` initializes interpreter state, oversampling scales, path/imager/font pointers, control stack, hint state, paint type, and grid-fitting flags.
- `gs_type1_finish_init` prepares fixed CTM coefficients, records character origin, initializes flex/hint offsets, computes character flatness, and marks initialization complete.
- `gs_type1_sbw`, `gs_type1_set_lsb`, and `gs_type1_set_width` set side bearing and width metrics.
- `gs_type1_blend` handles Multiple Master blend values using the font `WeightVector`.
- `gs_type1_seac` starts composite-accent handling by requesting the base character charstring.
- `gs_type1_endchar` either switches from base to accent charstring for `seac`, tolerates missing accent glyphs with a warning, or finalizes fill/flatness state.
- `type1_cis_get_metrics` exports left side bearing and width.
- `gs_type1_piece_codes` scans a Type 1 charstring looking for `seac`, following subroutines and selected othersubr patterns.
- `gs_type1_glyph_info` combines default glyph info, optional `seac` piece extraction, and width/vector extraction by partially interpreting the charstring.
- `gs_font_parent` returns a Type 9 parent font for encrypted Type 1/2 fonts when present.

Dependencies:
- Type 1 font internals from `gxfont1.h` and `gxtype1.h`.
- Charstring constants from `gsccode.h`.
- Matrix, imager, path, hinting, and fixed arithmetic helpers.

Research notes:
- `gs_type1_piece_codes` duplicates parsing logic rather than reusing the full interpreter; comments acknowledge this is unfortunate but simpler than refactoring.
- Some error paths in `gs_type1_glyph_info` return before freeing acquired glyph data, so callers should be cautious around malformed fonts or failed partial interpretation.
- `seac` accent-missing behavior intentionally follows Acrobat-like tolerance by skipping the missing accent without failing the whole glyph.
