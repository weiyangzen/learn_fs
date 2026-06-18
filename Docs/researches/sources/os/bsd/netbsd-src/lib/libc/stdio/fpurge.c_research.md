# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fpurge.c

Read completely: 75 lines.

This file implements `fpurge`, which discards buffered input/output without writing it. It rejects unopened streams, frees ungetc and wide I/O state, resets buffer pointers and counters, and preserves line/unbuffered write sizing rules.

Important interactions: manipulates core `FILE` buffering fields directly.

Security/reliability notes: unlike `fflush`, pending output is dropped; this is an intentional nonstandard behavior.
