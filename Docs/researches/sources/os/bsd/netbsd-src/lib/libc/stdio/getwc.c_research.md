# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/getwc.c

Provides a function version of the `getwc` macro. It simply delegates to `fgetwc(fp)`.

All wide-character decoding, orientation, locking, and error handling live in the underlying wide I/O implementation.
