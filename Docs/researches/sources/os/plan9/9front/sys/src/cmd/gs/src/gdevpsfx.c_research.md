# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsfx.c

This file converts Type 1 charstrings to unencrypted Type 2 charstrings. It expands Subrs inline and attempts several Type 2 operator optimizations.

Parsing layer:
- `type1_next_init` initializes a Ghostscript Type 1 interpreter state over a glyph data buffer.
- `skip_iv` skips/decrypts initial encrypted charstring bytes according to `lenIV`.
- `type1_next` parses numbers and operators, executes `callsubr`/`return`, handles `div`, blend OtherSubrs, pop suppression, and reports relevant operators to the converter.
- `type1_callsubr` loads local Subr data onto the Type 1 instruction stack.

Hint handling:
- `cv_stem_hint_table` stores horizontal and vertical stem hints, including replacement state.
- `type1_stem1` and `type1_stem3` collect and deduplicate hints, keeping them ordered.
- The converter first scans the charstring to gather all hints and detect whether hint replacement/dotsection handling is needed.
- The second pass emits initial stems and hint masks when active hints change.

Output layer:
- `type2_put_op`, `type2_put_int`, and `type2_put_fixed` encode Type 2 operators and operands.
- `type2_put_stems` emits compact stem hint data.
- `type2_put_hintmask` emits a hintmask operator plus active-hint bits.

Main entry point:
- `psf_convert_type1_to_type2` performs two passes. It handles width normalization, `hsbw`/`sbw`, moveto adjustment, `seac` conversion through Type 2 `endchar` operands, flex OtherSubrs, dotsection replacement, stem replacement, and path operators.

Optimizations:
- Combines repeated `rlineto`, `rrcurveto`, `hlineto`, `vlineto`, `hvcurveto`, and `vhcurveto` patterns.
- Converts eligible curves to `hhcurveto`, `vvcurveto`, `rlinecurve`, or `rcurveline`.
- Delays operator emission while tracking operand-stack depth to avoid overflowing Type 2 stack limits.

Notable limits:
- General unsupported OtherSubrs produce `rangecheck`.
- Subrs are expanded inline rather than preserved.
- The code has explicit comments for unimplemented counter control and possible future curve optimizations.
