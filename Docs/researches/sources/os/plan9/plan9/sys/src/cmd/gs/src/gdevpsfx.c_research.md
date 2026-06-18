# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsfx.c

This file converts Type 1 charstrings to unencrypted Type 2 charstrings. The converter expands local Subrs inline, collects hints, rewrites Type 1-only constructs, and opportunistically uses compact Type 2 operators.

Parsing layer:
- `type1_next_init` initializes a Ghostscript Type 1 interpreter state over one glyph data buffer.
- `skip_iv` decrypts/skips initial charstring random bytes according to `lenIV`.
- `type1_next` parses operands/operators, executes `callsubr` and `return`, handles `div`, blend OtherSubrs, pop suppression, and reports relevant operators to the converter.
- `type1_callsubr` loads local Subr data onto the Type 1 instruction stack.

Hint handling:
- `cv_stem_hint_table` stores horizontal and vertical stem hints, replacement state, and hint indices.
- `type1_stem1` and `type1_stem3` collect ordered/deduplicated hints.
- The first pass over the charstring gathers all hints and detects hint replacement/dotsection use.
- The second pass emits initial stem operators and `hintmask` bytes when active hints change.

Output layer:
- `type2_put_op`, `type2_put_int`, and `type2_put_fixed` encode Type 2 operators and operands.
- `type2_put_stems` emits compact stem hint data while respecting operand stack limits.
- `type2_put_hintmask` writes hintmask operators and active-hint bitmaps.

`psf_convert_type1_to_type2` is the main entry point. It handles width normalization from `hsbw`/`sbw`, initial side-bearing adjustment, moveto conversion, `seac` conversion through Type 2 `endchar` operands, flex OtherSubrs, dotsection replacement, stem replacement, and path operators.

Optimizations include combining repeated or compatible `rlineto`, `rrcurveto`, `hlineto`, `vlineto`, `hvcurveto`, and `vhcurveto` sequences; converting eligible curves to `hhcurveto` or `vvcurveto`; and using `rlinecurve`/`rcurveline` when a line/curve sequence permits it.

Notable limits:
- General unsupported OtherSubrs return `rangecheck`.
- Subrs are expanded inline rather than preserved.
- Counter control OtherSubrs are acknowledged but not implemented.
- Several comments identify further curve optimizations that were intentionally left out.
