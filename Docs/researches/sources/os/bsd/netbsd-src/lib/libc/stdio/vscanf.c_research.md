# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vscanf.c

Implements `vscanf()` and `vscanf_l()` as direct calls to `__svfscanf(stdin, ...)` and `__svfscanf_l(stdin, loc, ...)`. All scan parsing is delegated to `vfscanf.c`.

The locale variant is weak-aliased as `vscanf_l -> _vscanf_l`.
