# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfixed.h

## Purpose
Defines Ghostscript's internal fixed-point coordinate representation and conversion/rounding macros.

## Representation
- `fixed` is `long`.
- `ufixed` is `ulong`.
- Uses 8 fractional bits via `_fixed_shift`.
- `fixed_scale` is 256, so `fixed_1` is one device/user coordinate unit in fixed representation.
- Provides `gs_fixed_point` and `gs_fixed_rect`.

## Conversion Macros
Includes conversions between fixed and int/long/float:
- `int2fixed`
- `fixed2int`, `fixed2int_rounded`, `fixed2int_ceiling`, `fixed2int_pixround`
- variable optimized forms such as `fixed2int_var`
- `float2fixed`, `float2fixed_rounded`, `fixed2float`

## Rounding Model
Defines special pixel rounding for Ghostscript's center-of-pixel fill rule:
- `_fixed_pixround_v`
- `fixed_pixround`
- `fixed2int_pixround`

## Arithmetic / Overflow
- `CHECK_SET_FIXED_SUM` detects fixed addition overflow and clamps result.
- Declares `fixed_mult_quo` for high-precision `A * B / C`.
- Provides optional FPU-free helpers for float/double to fixed conversion under `USE_FPU_FIXED`.

## Integration
This header is foundational for path geometry, fill scan conversion, glyph outlines, and rasterization decisions.
