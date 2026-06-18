# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdio/compat_fgetpos.c

Read completely: 64 lines.

This implements old `fgetpos` using `off_t *` instead of current `fpos_t`. It asserts non-null arguments, stores `ftello(fp)` into `*pos`, and returns nonzero if `ftello` returned `(off_t)-1`.

Important interactions: binds legacy `fgetpos` to current offset-based stream positioning.

Security/reliability notes: simple wrapper. The return expression both assigns and checks for failure, relying on `ftello` to set errno.
