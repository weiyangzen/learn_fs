# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/tmpfile.c

Implements `tmpfile()`. It constructs a template in `_PATH_TMP`, blocks all signals while calling `mkstemp()` and immediately unlinking the name, restores the signal mask, then wraps the fd with `fdopen(fd, "w+")`.

If `fdopen()` fails, it closes the fd and restores the saved `errno`. The unlink-after-create pattern yields an unnamed temporary file that is removed automatically when closed.
