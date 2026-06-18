# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcsncasecmp.c

Implements `wcsncasecmp()` and `wcsncasecmp_l()`. It compares up to `n` wide characters after locale-aware lowercasing with `towlower_l()`, stopping on difference, NUL, or count exhaustion.

The non-locale form uses the current locale.
