# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/nrand.c

This file returns bounded pseudo-random ints.

Key behavior:
- `nrand` scales `lrand()` into `[0, n)`.

Important details:
- Integer counterpart to `lnrand`.
