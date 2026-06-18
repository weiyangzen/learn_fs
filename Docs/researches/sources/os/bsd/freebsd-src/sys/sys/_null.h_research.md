# File Research: sources/os/bsd/freebsd-src/sys/sys/_null.h

Portable `NULL` definition.

Key elements:
- Defines `NULL` only if not already defined.
- Uses `((void *)0)` for C.
- Uses `__null` for modern GNU C++, otherwise `0L` on LP64 C++ or `0`.

Dependencies:
- Compiler/language predefined macros.

Research notes:
- Small compatibility header used by other public headers that need `NULL` without pulling larger standard headers.
