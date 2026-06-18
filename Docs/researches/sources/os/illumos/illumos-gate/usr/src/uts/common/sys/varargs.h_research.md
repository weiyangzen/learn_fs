# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/varargs.h

## Role

Defines Solaris system variable-argument macros in terms of the shared `sys/va_impl.h` implementation.

## Key Interfaces

- Includes `sys/va_impl.h`.
- Defines `va_list` as `__va_list` when `_VA_LIST` is not already defined.
- Maps `va_start`, `va_arg`, `va_copy`, and `va_end` directly to `__va_start`, `__va_arg`, `__va_copy`, and `__va_end`.

## Design Notes

Despite the file name, it explicitly provides stdarg-style semantics rather than old K&R varargs semantics.

## Risk Notes

This header is part of the compiler/standard-library ABI surface. Macro definitions must remain synchronized with `va_impl.h` and `va_list.h`.
