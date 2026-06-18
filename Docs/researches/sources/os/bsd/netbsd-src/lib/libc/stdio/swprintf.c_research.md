# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/swprintf.c

Implements `swprintf()` and `swprintf_l()` as variadic wrappers over `vswprintf()` and `vswprintf_l()`. They pass the destination wide buffer, capacity, optional locale, format, and `va_list` to the underlying implementation.

The file provides the weak alias `swprintf_l -> _swprintf_l`.
