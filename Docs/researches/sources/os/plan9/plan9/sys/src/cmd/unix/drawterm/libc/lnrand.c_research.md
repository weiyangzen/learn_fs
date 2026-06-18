# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/lnrand.c

This file returns bounded non-negative pseudo-random longs.

Key behavior:
- `lnrand` scales `lrand()` into `[0, n)`.

Important details:
- Uses simple modulo/scaling logic from Plan 9 libc style.
