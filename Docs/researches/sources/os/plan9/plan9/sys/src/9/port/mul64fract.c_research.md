# File Research: sources/os/plan9/plan9/sys/src/9/port/mul64fract.c

Purpose: Portable C fallback for `mul64fract`, returning the middle 64 bits of a 64x64 -> 128-bit product.

Key logic:
- Splits both 64-bit operands into high/low 32-bit halves.
- Accumulates the middle product terms:
  `hi(al*bl) + al*bh + ah*bl + lo-shifted ah*bh`.
- Stores the fixed-point product result in `*r`.

Dependencies and integration:
- Includes `<u.h>` for `uvlong`.
- Intended to be replaced by architecture-specific assembler where available.

Risks and notes:
- Written for fixed-point multiplication where one operand’s integer portion is in the high word and fraction in the low word.
