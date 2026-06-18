# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/snprintf_ss.c

Implements `snprintf_ss()` as a variadic wrapper over `vsnprintf_ss()`. It initializes a `va_list`, delegates, and returns the result.

The `_ss` behavior is supplied by `vsnprintf_ss()` declared through `extern.h`; this file only exposes the convenient variadic entry point and weak alias.
