# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/flags.c

Read completely: 122 lines.

This file implements `__sflags`, translating stdio mode strings into internal `FILE` flags and `open(2)` flags. It supports `r`, `w`, `a`, `+`, `b`, and NetBSD extensions `e` for close-on-exec, `f` for regular-file-only, `l` for no symlink following, and `x` for exclusive creation.

Important interactions: used by `fopen`, `fdopen`, `freopen`, and `fmemopen`.

Security/reliability notes: invalid leading mode returns `EINVAL`; unknown trailing mode characters are ignored for compatibility.
