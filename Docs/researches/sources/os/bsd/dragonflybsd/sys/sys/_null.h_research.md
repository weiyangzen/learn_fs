# File Research: sources/os/bsd/dragonflybsd/sys/sys/_null.h

Read completely: 41 lines.

This header defines `NULL` if it is not already defined.

Key behavior:
- In C, `NULL` is `((void *)0)`.
- In GNU C++ 4+, `NULL` is `__null`.
- Otherwise, C++ receives integer `0`.

Security/reliability notes:
- No runtime behavior. The conditional definitions preserve C/C++ compatibility and avoid redefining existing `NULL`.
