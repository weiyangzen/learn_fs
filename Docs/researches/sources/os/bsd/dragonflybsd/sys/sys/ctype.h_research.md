# File Research: sources/os/bsd/dragonflybsd/sys/sys/ctype.h

Kernel-only lightweight ASCII ctype macro header.

Key responsibilities:
- Defines kernel macros for `isspace`, `isascii`, `isupper`, `islower`, `isalpha`, `isdigit`, `isxdigit`, and `isprint`.
- Defines ASCII-only `toupper` and `tolower`.

Dependencies:
- Active only under `_KERNEL`.

Notable risks:
- Macros evaluate arguments more than once in some cases, so callers should avoid side-effect expressions.
- Behavior is ASCII-only and not locale-aware.
