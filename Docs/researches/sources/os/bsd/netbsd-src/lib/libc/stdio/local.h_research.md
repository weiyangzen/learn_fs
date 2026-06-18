# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/local.h

Central internal header for NetBSD libc stdio. It declares private stream lifecycle, buffer, read/write/seek/close, scanf/printf, wide I/O, getdelim, fgetstr, locking, and cleanup functions.

Important macros include `cantwrite()`, ungetc-buffer detection/freeing (`HASUB`, `FREEUB`), fgetstr buffer cleanup (`FREELB`), and `__long_overflow()`. This file is the shared contract between the small public wrappers and the substantial stdio engines.
