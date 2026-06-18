# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/frand.c

This file returns floating-point pseudo-random values.

Key behavior:
- `frand` scales `lrand()` into the range `[0, 1)`.

Important details:
- Uses a 31-bit mask and normalization constant.
