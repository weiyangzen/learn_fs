# File Research: sources/os/bsd/netbsd-src/sys/sys/ieee754.h

Read completely: 218 lines.

## Purpose
Defines bitfield layouts and helper unions for IEEE-754 single, double, and optional 128-bit long-double formats.

## Main Interfaces
- Precision constants: `SNG_EXPBITS`, `SNG_FRACBITS`, `DBL_EXPBITS`, `DBL_FRACHBITS`, `DBL_FRACLBITS`, optional `EXT_*`.
- Layout structs: `ieee_single`, `ieee_double`, optional `ieee_ext`, endian-dependent.
- Infinity/NaN exponents: `SNG_EXP_INFNAN`, `DBL_EXP_INFNAN`, optional `EXT_EXP_INFNAN`.
- Biases: `SNG_EXP_BIAS`, `DBL_EXP_BIAS`, optional `EXT_EXP_BIAS`.
- Unions: `ieee_single_u`, `ieee_double_u`, optional `ieee_ext_u`.
- Access macros and zero-fraction predicates.
- `EXT_TO_ARRAY32` for 128-bit long double fraction extraction.

## Dependencies And Integration
Includes machine endian definitions and expects machine headers to define long-double support when relevant.

## Risks And Edge Cases
- Bitfield layout is endian-dependent and compiler ABI-sensitive.
- 128-bit long double support appears only when `__HAVE_LONG_DOUBLE == 128`.
- `SNGU_ZEROFRAC_P`/`DBLU_ZEROFRAC_P` names test nonzero fraction despite “ZEROFRAC” wording.

## Filesystem Relevance
Low. General numeric ABI support; no direct filesystem behavior.
