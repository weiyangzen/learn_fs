# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/putwc.c

Provides a function version of the `putwc` macro. It delegates directly to `fputwc(wc, fp)`.

All wide output conversion and stream state handling is in the underlying wide stdio implementation.
