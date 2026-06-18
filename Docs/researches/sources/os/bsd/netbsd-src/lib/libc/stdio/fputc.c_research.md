# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fputc.c

Read completely: 59 lines.

This file implements `fputc`. It locks the stream, writes one character through `__sputc`, unlocks, and returns the result.

Important interactions: function wrapper for the byte-output macro path.

Security/reliability notes: buffering and errors are delegated to `__sputc`.
