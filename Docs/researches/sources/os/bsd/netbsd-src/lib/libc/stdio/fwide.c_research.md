# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fwide.c

Read completely: 72 lines.

This file implements `fwide`. It normalizes mode to -1, 0, or 1, locks the stream, obtains wide I/O state, sets orientation if it was previously undecided and the requested mode is nonzero, then returns the resulting orientation.

Important interactions: byte and wide I/O functions also set orientation through internal macros.

Security/reliability notes: if `WCIO_GET(fp)` fails, this implementation returns 0 while still inside the locked section, which appears to risk leaving the stream locked.
