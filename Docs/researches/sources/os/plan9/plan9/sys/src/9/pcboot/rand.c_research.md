# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/rand.c

This file provides lightweight pseudo-random support for the bootstrap environment.

Key responsibilities:
- Stubs `randomread` and `randominit` because the full kernel random device is not present.
- Implements libc-style `srand` and `lrand` without locks.
- Uses the Mitchell/Reeds lagged Fibonacci generator initialized by a Park-Miller sequence.

Filesystem/storage relevance:
- Used by boot networking for ephemeral local ports and retry variation.
- Not cryptographic and not suitable for security-sensitive filesystem or auth randomness.
