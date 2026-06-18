# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gxfrac.h

## Purpose
Defines Ghostscript's compact fractional color representation and conversion helpers.

## Representation
- `frac` and `signed_frac` are `short`.
- Uses 15 effective bits.
- `frac_1` is `0x7ff8`, deliberately chosen so common fractions can be represented more exactly than with a full `32767` scale.

## Conversion Helpers
- `frac2float`
- `float2frac`
- `frac2bits`
- `bits2frac`
- `frac2byte`
- `byte2frac`
- `frac2bits_floor`
- `frac2ushort`
- `ushort2frac`

## Arithmetic Helpers
- `frac_1_quo`: quotient for product divided by `frac_1`.
- `frac_1_rem`: remainder after that quotient.

## Integration
Used by transfer maps, color mapping, halftoning, and other internal color calculations.
