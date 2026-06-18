# File Research: sources/os/plan9/9front/sys/src/9/omap/fpi.c

Software floating-point internal arithmetic routines.

Key behavior:
- Operates on `Internal` extended representations from `fpi.h`.
- Provides rounding, exponent matching, normalization, renormalization, add, subtract, multiply, divide, and compare.
- Handles zero, infinity, and NaN cases through `fpi.h` macros.
- Multiplication splits significands into chunks for portable integer arithmetic.
- Division implements a bit-building quotient loop over the internal fraction width.

Research notes:
- Arithmetic is used by ARM FPA/VFP emulation in `fpiarm.c`.
- The implementation targets kernel portability and avoids relying on hardware floating point.
