# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vsnprintf.c

Implements `vsnprintf_l()`, `vsnprintf()`, `snprintf()`, and `snprintf_l()`. `vsnprintf_l()` builds a string-output `FILE` over the caller buffer, leaves room for a terminating NUL when `n > 0`, uses a dummy zero-sized buffer when `n == 0`, calls `__vfprintf_unlocked_l()`, then writes the final NUL at the current pointer.

It rejects sizes greater than `INT_MAX` with `EOVERFLOW`. The non-locale variants use `_current_locale()`, and weak aliases provide underscored libc symbol names.
