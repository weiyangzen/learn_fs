# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/libc/rand.c

This file implements libc `rand`.

Key behavior:
- `rand` returns the low 15-bit style value from `lrand`.

Important details:
- Thin compatibility wrapper.
