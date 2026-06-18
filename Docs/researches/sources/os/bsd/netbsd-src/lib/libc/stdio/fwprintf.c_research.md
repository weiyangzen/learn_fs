# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fwprintf.c

Implements the variadic wide-character formatted output entry points `fwprintf()` and `fwprintf_l()`. Both build a `va_list`, delegate to `vfwprintf()` or `vfwprintf_l()`, then return the delegated result.

This is a thin public API wrapper around the real wide printf engine in `vfwprintf.c`. It provides the locale-specific weak alias `fwprintf_l -> _fwprintf_l`.
