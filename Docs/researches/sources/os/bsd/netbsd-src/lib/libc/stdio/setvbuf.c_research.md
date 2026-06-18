# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/setvbuf.c

Implements `setvbuf()`, the main buffering reconfiguration routine. It validates mode and implementation-size limits, locks the stream, flushes pending output, frees ungetc and wide I/O state, discards unread input, clears EOF, frees malloc-owned old buffers, and rebuilds flags and buffer pointers.

For buffered modes it asks `__swhatbuf()` for optimal I/O sizing, allocates a buffer if the caller did not provide one, falls back to unbuffered mode on allocation failure, and adjusts write counters for line/full buffering. It also disables seek optimization when the chosen buffer size is not the filesystem block size.
