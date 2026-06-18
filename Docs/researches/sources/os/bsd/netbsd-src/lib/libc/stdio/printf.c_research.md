# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/printf.c

Implements `printf()` and `printf_l()` as variadic wrappers over `vfprintf(stdout, ...)` and `vfprintf_l(stdout, loc, ...)`. The actual formatting engine lives in the included/compiled `vfwprintf.c` implementation.

It provides the locale-specific weak alias `printf_l -> _printf_l`.
