# File Research: sources/os/bsd/netbsd-src/lib/libutil/strpct.c

## Purpose
Formats unsigned and signed ratios as percentage-like decimal strings without floating point.

## Key Details
- Global rounding mode set by `strpct_round`.
- `strpct`/`strpct_r` handle unsigned numerator and denominator.
- `strspct`/`strspct_r` handle signed inputs and sign-aware rounding.
- Uses a small two-part bignum to avoid overflow while generating decimal digits.
- Denominator zero is treated as one.
- Honors locale decimal point.

## Dependencies and Role
- Numeric formatting utility.
