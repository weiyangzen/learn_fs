# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/setbuffer.c

Implements BSD `setbuffer()` and `setlinebuf()`. `setbuffer()` delegates to `setvbuf()` with full buffering when a buffer is provided or unbuffered mode otherwise; `setlinebuf()` requests line buffering with an internally allocated buffer.

All actual buffer teardown/allocation/state changes are handled in `setvbuf.c`.
