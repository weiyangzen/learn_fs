# File Research: sources/os/bsd/openbsd-src/sys/sys/_null.h

Purpose: Provides the `NULL` definition when not already defined.

Key behavior:
- Uses `((void *)0)` for C.
- Uses `nullptr` for C++11 and newer.
- Uses `__null` for GNU C++ where available, otherwise `0L`.

Filesystem relevance:
- General public header utility with no filesystem-specific logic.
