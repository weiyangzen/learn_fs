# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetc.c

Read completely: 61 lines.

This file implements `fgetc`. It locks the stream, calls `__sgetc(fp)`, unlocks, and returns the byte or EOF.

Important interactions: function wrapper for macro-style stdio byte input.

Security/reliability notes: refill and error handling are delegated to the internal `__sgetc` path.
