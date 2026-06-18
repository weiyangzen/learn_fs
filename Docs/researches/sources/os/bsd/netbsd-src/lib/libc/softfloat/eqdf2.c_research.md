# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/eqdf2.c

Read completely: 24 lines.

Defines GCC/libgcc helper `__eqdf2` for double-precision equality comparison. It includes the GCC softfloat namespace remapper and delegates to `float64_eq(a, b)`.

The return convention follows the libgcc comment: returns `!(a == b)`, so equal operands produce `0` and unequal/unordered operands produce nonzero according to `float64_eq` behavior.

Risk: tiny adapter; correctness depends on matching GCC comparison-helper return conventions.
