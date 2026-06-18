# File Research: sources/os/bsd/netbsd-src/lib/libc/string/wcscasecmp.c

Implements `wcscasecmp()` and `wcscasecmp_l()`. It lowercases each wide character with `towlower_l()`, compares the lowered values, and stops on difference or terminating NUL.

The non-locale variant uses `_current_locale()`.
