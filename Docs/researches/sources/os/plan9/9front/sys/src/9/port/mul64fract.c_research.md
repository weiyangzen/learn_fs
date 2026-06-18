# File Research: sources/os/plan9/9front/sys/src/9/port/mul64fract.c

Portable fallback implementation of 64-bit fixed-point fractional multiplication.

Key behavior:
- `mul64fract(r, a, b)` computes the middle 64 bits of a 128-bit product.
- Splits each operand into high/low 32-bit halves.
- Sums the cross-products corresponding to the middle result.

Role:
- Intended as a C fallback for ports without architecture assembly.
- Useful when one operand is a fixed-point number with integer bits in the high word and fractional bits in the low word.

Notable constraints:
- Comments explicitly prefer architecture-specific assembly versions where available.
