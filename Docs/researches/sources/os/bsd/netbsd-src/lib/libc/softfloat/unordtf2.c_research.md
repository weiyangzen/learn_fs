# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/unordtf2.c

Read completely: 32 lines.

This file conditionally implements `__unordtf2` for quad-precision `float128` values when `FLOAT128` is enabled. Like the other unordered helpers, it compares each operand with itself through `float128_eq` and returns true if either comparison is false.

Important interactions: compiler runtime ABI support for quad-precision soft-float comparisons.

Security/reliability notes: compiled out entirely when `FLOAT128` is not configured; both self-comparisons are preserved for signaling-NaN handling.
