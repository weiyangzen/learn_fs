# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/remove.c

Implements `remove(const char *file)`. It first `lstat()`s the path, then calls `rmdir()` for directories or `unlink()` for non-directories.

The explicit directory branch avoids relying on filesystem-specific behavior for `unlink(2)` on directories.
