# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/mktemp.c

Implements internal `_mktemp()` and public `mktemp()` as name-only calls to `GETTEMP(path, NULL, 0, 0, 0)`. Both mutate the template in place and return the path on success or `NULL`.

The public `mktemp()` emits a warning recommending `mkstemp()` or `mkdtemp()` because name-only temporary path generation is race-prone.
