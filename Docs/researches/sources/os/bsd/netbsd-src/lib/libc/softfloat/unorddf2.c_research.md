# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/unorddf2.c

Read completely: 28 lines.

This file implements the GCC helper `__unorddf2` for double-precision SoftFloat values. It returns true when either operand is unordered, detected by comparing each operand with itself using `float64_eq`.

Important interactions: included through `softfloat-for-gcc.h`, `milieu.h`, and `softfloat.h`; used as compiler runtime support on targets where libc supplies software floating-point helpers.

Security/reliability notes: both self-comparisons are intentionally evaluated so signaling NaNs are observed according to SoftFloat behavior.
