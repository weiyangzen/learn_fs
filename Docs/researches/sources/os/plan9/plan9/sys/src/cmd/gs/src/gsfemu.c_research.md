# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gsfemu.c

## Role

GCC soft-float support implementation for Ghostscript platforms lacking usable hardware floating point. It supplies compiler helper symbols for single and double precision arithmetic, comparison, and conversion.

## Main Data

Defines IEEE float/double bit extraction macros, endian-aware double word indexing, sign/exponent/mantissa helpers, and bit-level aliases for float/double arguments and results.

## Control Flow

Implements negation, addition/subtraction, multiplication, division, comparisons, int/float conversions, double/float conversion, and int-to-float conversions. Double multiplication uses 14-bit chunk products; division generates quotient bits iteratively. Overflow and divide-by-zero raise `SIGFPE`; many underflows return signed zero.

## Dependencies

Uses `std.h`, `<signal.h>`, architecture endianness macros, and compiler/runtime expectations for `__adddf3`, `__mulsf3`, `__fixdfsi`, etc.

## Notes

This is explicitly not a complete IEEE implementation: only round-to-nearest is attempted, NaNs are not properly handled, and denormal support is absent for several operations.
