# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/tempnam.c

Implements legacy `tempnam()`. It allocates a `MAXPATHLEN` buffer and tries candidate directories in order: `TMPDIR`, caller `dir`, `P_tmpdir`, then `_PATH_TMP`, generating `pfx + XXXXXXXXXX` names with `_mktemp()`.

It warns that `tempnam()` may be unsafe and recommends `mkstemp()` or `mkdtemp()`. On total failure it preserves `errno` across the final free.
