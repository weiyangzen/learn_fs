# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/flt_rounds.c

Read completely: 33 lines.

Implements `__flt_rounds`, mapping NetBSD `fpgetround()` results to C `FLT_ROUNDS` values. The mapping is nearest `1`, toward zero `0`, upward/downward as `2`/`3`, with an `__m68k__` swap for that platform's rounding-mode ordering.

Risk: depends on `fpgetround()` returning an in-range enum index.
