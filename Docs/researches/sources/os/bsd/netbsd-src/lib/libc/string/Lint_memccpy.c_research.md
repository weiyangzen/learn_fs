# File Research: sources/os/bsd/netbsd-src/lib/libc/string/Lint_memccpy.c

Read completely: 15 lines.

Lint-only stub for `memccpy(void *, const void *, int, size_t)`. It returns `NULL` after marking parameters unused.

The actual byte-copy-until-character logic is in `memccpy.c`.
