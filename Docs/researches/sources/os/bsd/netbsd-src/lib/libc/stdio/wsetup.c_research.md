# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/wsetup.c

Read completely: 99 lines.

Implements `__swsetup(FILE *fp)`, which prepares a stream for writing. It initializes stdio if needed, transitions read/write streams from read mode to write mode by clearing read and EOF state and freeing ungetc data, creates a buffer with `__smakebuf()` if absent, and sets `_w`/`_lbfsize` according to line, unbuffered, or fully buffered mode.

It returns `EOF` if the stream is not writable and not read/write. This is a central setup helper for output paths that detect missing `__SWR` or missing buffers.
