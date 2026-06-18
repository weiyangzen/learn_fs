# File Research: sources/os/bsd/netbsd-src/lib/libbsdmalloc/Makefile

Builds the legacy BSD malloc library.

Key behavior:
- Builds `LIB=bsdmalloc` from `malloc.c`.
- Installs `bsdmalloc.3`.
- Disables compiler builtin assumptions for aligned allocation, calloc, free, malloc, posix_memalign, and realloc.
- Defines `_REENT` and `_REENTRANT`.
- Includes libc private headers for reentrant locking support.

Dependencies:
- NetBSD libc internal `reentrant.h`.
