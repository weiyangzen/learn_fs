# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/putwchar.c

Provides a function version of `putwchar()`. It writes the given wide character to `stdout` via `fputwc(wc, stdout)`.

The file is a minimal stdout wrapper for wide-character output.
