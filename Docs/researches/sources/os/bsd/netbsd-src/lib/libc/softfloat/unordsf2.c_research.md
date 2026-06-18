# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/unordsf2.c

Read completely: 28 lines.

This file implements the GCC helper `__unordsf2` for single-precision SoftFloat values. It reports unordered comparison status by evaluating `float32_eq(a, a)` and `float32_eq(b, b)` and inverting the combined ordered result.

Important interactions: provides compiler ABI support for soft-float single comparisons.

Security/reliability notes: the structure preserves signaling-NaN side effects by checking both operands rather than short-circuiting after the first NaN.
