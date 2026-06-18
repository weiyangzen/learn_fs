# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/makebuf.c

Implements stdio buffer selection and allocation through `__smakebuf()` and `__swhatbuf()`. `__swhatbuf()` uses `fstat()` to choose block-size-based buffering, determine whether a stream could be a tty, and enable or disable seek optimization.

`__smakebuf()` honors existing unbuffered flags, environment overrides via `STDBUF`/`STDBUF<fd>`, allocates buffers when possible, sets line buffering for ttys, and falls back to the one-byte unbuffered internal buffer on allocation failure. The environment syntax supports unbuffered, line-buffered, or fully-buffered modes plus an optional size up to 1 MiB.
