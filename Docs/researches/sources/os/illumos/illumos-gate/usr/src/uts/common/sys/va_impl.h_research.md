# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/va_impl.h

## Role

Common implementation layer for illumos variable argument support used by `stdarg.h`, `varargs.h`, ISO stdarg headers, and `sys/varargs.h`.

## Key Interfaces

- Documents common implementation macros: `__va_start`, `__va_arg`, `__va_copy`, and `__va_end`.
- Includes `sys/va_list.h` for `__va_list`, `__va_alist_type`, and ISA definitions.
- Provides lint protocol definitions.
- Provides protocol for compilers with `__BUILTIN_VA_STRUCT`, using `__builtin_va_start` and `__builtin_va_arg_incr`.
- Provides protocol for `__BUILTIN_VA_ARG_INCR`.
- Provides GCC 2.96+/3+ protocol using `__builtin_stdarg_start` or `__builtin_va_start`, `__builtin_va_arg`, `__builtin_va_end`, and `__builtin_va_copy`.
- Emits a compile-time error for unrecognized compiler protocols.

## Design Notes

The header centralizes compiler-specific handling while keeping user-facing namespace pollution out of standard headers.

## Risk Notes

Compiler feature detection is critical. Falling into the wrong protocol produces silent ABI corruption, so unknown compilers intentionally fail compilation.
