# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/stdio.h

Declares compatibility stdio file-position APIs.

It exposes old `fgetpos(FILE *, off_t *)` and `fsetpos(FILE *, const off_t *)`.

Filesystem relevance is direct through file stream positioning ABI.
