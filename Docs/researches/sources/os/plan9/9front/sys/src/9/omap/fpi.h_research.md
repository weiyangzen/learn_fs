# File Research: sources/os/plan9/9front/sys/src/9/omap/fpi.h

Header for the software floating-point internal format.

Key contents:
- Defines `Word`, `Single`, and `Double`.
- Defines fraction and exponent geometry: hidden bit, guard bit, carry bit, exponent bias, infinity exponent, and fraction width.
- Defines `Internal` as sign, exponent, low fraction, and high fraction fields.
- Macros identify and set weird values, infinity, NaN, and zero.

Research notes:
- The internal format supports the arithmetic core in `fpi.c`, memory conversions in `fpimem.c`, and instruction emulation in `fpiarm.c`.
