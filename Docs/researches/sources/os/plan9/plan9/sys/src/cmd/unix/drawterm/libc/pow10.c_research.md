# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/pow10.c

This file provides powers of ten for formatting/parsing.

Key behavior:
- `__fmtpow10` returns `10^n` using a static table for common exponents and repeated multiplication for larger values.

Important details:
- Used by floating-point formatting and parsing support.
