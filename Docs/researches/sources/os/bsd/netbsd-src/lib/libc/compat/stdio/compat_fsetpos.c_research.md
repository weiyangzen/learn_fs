# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdio/compat_fsetpos.c

Read completely: 68 lines.

This implements old `fsetpos` with an `off_t *` position. It asserts non-null arguments and calls `fseeko(iop, *pos, SEEK_SET)`.

Important interactions: provides compatibility for binaries expecting the older position type.

Security/reliability notes: the wrapper compares the `fseeko` return value to `(off_t)-1` even though `fseeko` returns `int`; this works for failure detection but mirrors historical style rather than modern type clarity.
