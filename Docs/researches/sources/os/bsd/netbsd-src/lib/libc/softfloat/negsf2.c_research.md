# File Research: sources/os/bsd/netbsd-src/lib/libc/softfloat/negsf2.c

Read completely: 24 lines.

Defines `__negsf2` for single-precision negation. It flips bit `0x80000000`.

Risk: pure bit operation; preserves payloads and handles `+0`/`-0` by toggling sign.
