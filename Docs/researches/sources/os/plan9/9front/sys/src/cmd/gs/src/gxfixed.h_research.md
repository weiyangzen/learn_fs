# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfixed.h

Defines Ghostscript’s fixed-point coordinate representation and conversion/arithmetic helpers.

Key definitions:
- `fixed` is a signed long; `ufixed` is an unsigned long.
- Fixed coordinates use 8 fractional bits (`fixed_scale == 256`).
- Provides constants such as `fixed_0`, `fixed_epsilon`, `fixed_1`, `fixed_half`, `max_fixed`, and `min_fixed`.
- Provides integer/float conversions, rounding, ceiling, floor, pixel rounding, fraction extraction, and truncation macros.
- Defines `CHECK_SET_FIXED_SUM` for overflow-detecting fixed addition.
- Declares `fixed_mult_quo` for safe `A * B / C` when products may exceed a long.
- Provides optional FPU-less IEEE helpers for float/double to fixed conversion.
- Defines `gs_fixed_point` and `gs_fixed_rect`.

Dependencies:
- Uses architecture macros such as `ARCH_SIZEOF_LONG`, `arch_ints_are_short`, `arch_is_big_endian`, and FPU-related feature flags.
- Uses Ghostscript error codes for limitcheck handling.

Research notes:
- Pixel rounding is central to the fill code’s center-of-pixel rule.
- The 8-bit fractional choice balances coordinate range with enough precision for rasterization.
- Many fill algorithms depend on the exact semantics of `fixed_pixround`, `fixed2int_pixround`, and `fixed_mult_quo`.
