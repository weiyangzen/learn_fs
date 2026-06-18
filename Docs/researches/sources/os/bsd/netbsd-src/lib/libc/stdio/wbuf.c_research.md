# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/wbuf.c

Read completely: 100 lines.

Implements `__swbuf(int c, FILE *fp)`, the slow path for writing one byte to a stdio output buffer. It sets byte orientation, checks write permission through `cantwrite()`, flushes a full buffer, stores the byte, and flushes again when the buffer becomes full or a line-buffered stream receives `'\n'`.

It deliberately resets `_w` to `_lbfsize` before checking writability so future `putc()` calls re-enter this path after errors or longjmp-like exits. On write-not-allowed it sets `errno = EBADF` and returns `EOF`.
