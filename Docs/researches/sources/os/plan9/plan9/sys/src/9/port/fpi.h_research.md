# File Research: sources/os/plan9/plan9/sys/src/9/port/fpi.h

Purpose: Type definitions, constants, macros, and prototypes for the floating-point interpreter.

Contents:
- Defines `Word`, `Vlong`, `Single`, and `Double` mapping to `FPdbleword`.
- Defines fraction, carry, hidden-bit, guard-bit, exponent-bias, and infinity constants.
- Defines `Internal` representation with sign, exponent, low fraction, and high fraction.
- Provides macros for zero, NaN, infinity tests and setters.
- Declares arithmetic routines from `fpi.c` and conversion routines from `fpimem.c`.

Dependencies and integration:
- Includes `<u.h>` if needed and assumes Plan 9 floating bit layout types.
