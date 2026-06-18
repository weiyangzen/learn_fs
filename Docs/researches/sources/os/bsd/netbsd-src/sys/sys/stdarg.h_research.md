# File Research: sources/os/bsd/netbsd-src/sys/sys/stdarg.h

Read completely: 68 lines.

This header defines `va_list` and standard varargs macros through compiler builtins. It has lint stubs, compatibility mapping to `__builtin_stdarg_start` for older GCC combinations, and exposes `va_start`, `va_arg`, `va_end`, `__va_copy`, and C99/NetBSD `va_copy`.

Risks: highly compiler-dependent. The fallback logic is constrained to specific GCC/Clang feature checks.
