# File Research: sources/os/bsd/freebsd-src/sys/sys/_stdarg.h

Compiler-backed variadic argument macros.

Key elements:
- Includes visibility macros.
- Defines `va_list` from `__builtin_va_list` if needed.
- Maps `va_start`, `va_arg`, `__va_copy`, `va_copy`, and `va_end` to compiler builtins.

Dependencies:
- Includes `sys/_visible.h`.

Research notes:
- `va_copy` is exposed for ISO C99 and newer.
- Centralizes stdarg behavior for FreeBSD headers.
