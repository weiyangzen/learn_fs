# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/div.c

Read completely: 81 lines.

Implements `div(int num, int denom)`. It computes quotient and remainder with machine `/` and `%`, then adjusts results if the platform division rounded toward negative infinity rather than toward zero.

The correction path triggers when `num >= 0 && r.rem < 0`, incrementing quotient and subtracting denominator from remainder to satisfy ANSI/C quotient truncation requirements.
