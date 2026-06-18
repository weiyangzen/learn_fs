# File Research: sources/os/bsd/openbsd-src/sys/sys/varargs.h

Implements traditional pre-ANSI varargs macros for GNU C. It maps `va_alist`, `va_dcl`, `va_start`, `va_end`, `va_arg`, and `__va_copy` to compiler builtins and defines `va_list`.

This is legacy compatibility surface. New code should normally use `stdarg.h`, but this header preserves K&R-style varargs consumers.
