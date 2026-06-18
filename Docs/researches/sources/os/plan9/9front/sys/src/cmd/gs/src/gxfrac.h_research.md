# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxfrac.h

Defines Ghostscript’s compact fractional color/value representation.

Key definitions:
- `frac` and `signed_frac` are signed shorts.
- Uses 15 effective bits with endpoint `frac_1 == 0x7ff8`.
- Chooses a range that exactly represents many common fractions better than a full signed-short range.
- Provides conversions between fracs and floats, bytes, arbitrary bit widths, unsigned shorts, and products/quotients by `frac_1`.
- Defines `frac_1_quo` and `frac_1_rem` helpers for scaled integer math.

Dependencies:
- Relies on architecture short-size macros.

Research notes:
- This representation is used in color transfer maps and raster color math.
- The non-maximal endpoint value is intentional to reduce common rounding errors.
