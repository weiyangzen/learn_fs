# File Research: sources/os/bsd/openbsd-src/sys/sys/limits.h

Defines machine-independent C/POSIX scalar limits layered over `<machine/limits.h>`.

Key contents:
- Character, short, int, long, and long long min/max constants.
- `MB_LEN_MAX` set to 4 for UTF-8.
- BSD-visible `UID_MAX` and `GID_MAX`.
- XPG/POSIX `LONG_BIT` and `WORD_BIT`.
- Legacy XSI float constants via `<machine/_float.h>` for older visibility levels.

Risk notes:
- Values are ABI/compiler-visibility sensitive, especially `__LP64__`, `__CHAR_UNSIGNED__`, and standards visibility macros.
