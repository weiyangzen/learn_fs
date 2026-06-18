# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/templates/softfloat.h

Read completely: 290 lines.

Template version of the SoftFloat public header. It enables `FLOATX80` and `FLOAT128`, defines software FP types (`float32`, `float64`, optional `floatx80`, optional `float128`) with placeholder integer type tokens, declares global tininess/rounding/exception state, exception flag constants, `float_raise`, and all conversion/arithmetic/comparison APIs for single, double, extended, and quadruple precision.

The placeholder tokens such as `!!!bits32`, `!!!int8`, and `!!!flag` indicate this file is processed to create architecture-specific usable headers.

Risk: API contract file rather than executable logic. Any mismatch between generated prototypes here and implementations in `softfloat.c` or GCC remaps in `softfloat-for-gcc.h` would break soft-float ABI compatibility.
