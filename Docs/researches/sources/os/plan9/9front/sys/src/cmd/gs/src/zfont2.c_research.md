# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfont2.c

## Purpose
Builds Type 2 / CFF CharString fonts.

## Key Functions
- `subr_bias()` computes CFF local/global subroutine bias from subroutine count.
- `type2_font_params()` sets Type 2 interpreter parameters, reads `GlobalSubrs`, width defaults, and random seed.
- `zbuildfont2()` builds a Type 2 font using `%Type2BuildChar` and `%Type2BuildGlyph`.

## Important Behavior
- Type 2 fonts use `gs_type2_interpret`, default `lenIV` 0, and CFF subroutine bias rules.
- `GlobalSubrs` must be an array if present.
- `defaultWidthX` and `nominalWidthX` are converted to fixed-point values.
- `initialRandomSeed` is optional but must be integer if present.

## Research Notes
This file relies on the Type 1 shared CharString builder from `zfont1.c`.
