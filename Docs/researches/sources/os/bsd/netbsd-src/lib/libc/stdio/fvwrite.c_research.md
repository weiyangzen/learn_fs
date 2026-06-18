# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fvwrite.c

Read completely: 236 lines.

This file implements `__sfvwrite`, the central vector write engine. It validates residual size, checks write capability, and handles unbuffered, fully buffered, string-buffer, auto-growing string, and line-buffered streams, writing directly or copying into the stream buffer as appropriate.

Important interactions: used by `fputs`, `fputwc`, formatted output, and other output helpers.

Security/reliability notes: write failures set `__SERR`. The code caps direct writes at `INT_MAX` and treats string output specially so snprintf-style streams can report required length without necessarily writing all bytes.
