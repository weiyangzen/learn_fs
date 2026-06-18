# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxtype1.c

Shared Adobe Type 1 / Type 2 charstring interpreter support for Ghostscript fonts.

Key behavior:
- Defines GC enumeration/relocation for `gs_type1_state`, including relocation of saved charstring instruction pointers relative to relocated glyph data.
- Exports `gx_extendeg_glyph_name_separator`, used by PDF font logic to resolve glyph-name conflicts while converting widths to metrics.
- `gs_type1_interp_init` initializes interpreter state, operand/control stacks, font/imager/path pointers, callback data, paint type, hinting flags, oversampling scales, sidebearing/width state, and seac state.
- `gs_type1_finish_init` computes fixed CTM coefficients, records path origin, initializes hint/flex offsets, and derives character flatness.
- `gs_type1_sbw`, `gs_type1_set_lsb`, and `gs_type1_set_width` record side bearing and width metrics.
- `gs_type1_blend` blends Multiple Master font values using the font weight vector.
- `gs_type1_seac` begins composite accented-character handling by saving accent/base operands and loading the base CharString.
- `gs_type1_endchar` switches from base to accent CharString for `seac`, handles missing accent glyphs compatibly, adjusts fill state for PaintType 0, and sets flatness unless grid fitting is disabled.
- `type1_cis_get_metrics` returns lsb and width as doubles.
- `gs_type1_piece_codes` partially decodes a Type 1 CharString to detect `seac` piece character codes, including subroutine calls and selected OtherSubrs.
- `gs_type1_glyph_info` combines default glyph info with piece and width extraction by fetching glyph data and interpreting until `[h]sbw`.
- `gs_font_parent` returns a Type 1/Type 2 font’s parent Type 9 font when present.

Notable dependencies:
- Font internals: `gxfont.h`, `gxfont1.h`, `gxtype1.h`.
- Charstring constants and glyph data: `gsccode.h`, `gsgdata.h`.
- Hinting and path support: `gxhintn.h`, `gxchrout.h`, `gzpath.h`.

Research notes:
- `gs_type1_piece_codes` duplicates part of the charstring parser because factoring it out was considered too invasive.
- `gs_type1_glyph_info` returns `rangecheck` for unknown OtherSubr during width extraction because it cannot safely continue.
- The missing seac accent path prints a warning and skips the missing accent, matching Acrobat Reader behavior per the comment.
