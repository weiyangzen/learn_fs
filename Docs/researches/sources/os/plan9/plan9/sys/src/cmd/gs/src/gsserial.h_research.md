# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsserial.h

## Purpose
Declares and macro-optimizes compact serialization of unsigned and signed integers, including point pairs, for Ghostscript command-list and object serialization code.

## Public Surface
- Unsigned constants: `enc_u_shift`, `enc_u_lim_1b`, `enc_u_lim_2b`, `enc_u_sizew_max`.
- Unsigned sizing macros: `enc_u_sizew`, `enc_u_size2w`, `enc_u_sizexy`.
- Unsigned put/get macros: `enc_u_putw`, `enc_u_put2w`, `enc_u_putxy`, `enc_u_getw`, `enc_u_getw_nc`, `enc_u_get2w`, `enc_u_get2w_nc`, `enc_u_getxy`, `enc_u_getxy_nc`.
- Signed constants: `enc_s_shift0`, `enc_s_shift1`, one-byte/min/max limits, `enc_s_min_int`, `enc_s_sizew_max`.
- Signed sizing and put/get macros: `enc_s_sizew`, `enc_s_sizexy`, `enc_s_putw`, `enc_s_putxy`, `enc_s_getw`, `enc_s_getw_nc`, `enc_s_getxy`, `enc_s_getxy_nc`.
- Function prototypes for slow-path size, encode, and decode routines implemented in `gsserial.c`.

## Implementation Pattern
- Fast macros handle one- and two-byte unsigned cases inline before dispatching to functions for larger values.
- Signed macros inline the single-byte range and use functions for larger values.
- Separate `_nc` decode variants exist because many call sites use const byte pointers but some mutate pointer variables of non-const type.

## Dependencies
Requires Ghostscript `byte`, `uint`, `int`, point-like `.x/.y` structs, and `BEGIN`/`END` macro conventions from included base headers.

## Risks and Notes
- The signed-format documentation has obvious typos (`x >- 0`, multiplication where shift is intended), but the macros and implementation define the actual behavior.
- These macros evaluate pointer arguments mutably and should only be used with lvalue pointer variables.
