# File Research: sources/os/bsd/netbsd-src/lib/libc/quad/TESTS/divrem.c

Interactive test driver for `__qdivrem()`. It reads two 64-bit values as high/low 32-bit words in decimal or hex, calls `__qdivrem()` to compute quotient and remainder, and prints both word-pair and concatenated hex results.

The program uses old-style K&R `main()` and calls `exit(0)` without including `<stdlib.h>`, reflecting its historical/manual-test nature. It assumes the union layout of `long long` and two `unsigned int` words matches the target’s expected display order.
