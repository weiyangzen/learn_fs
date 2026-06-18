# File Research: sources/os/bsd/netbsd-src/lib/libc/string/strsignal.c

Implements public `strsignal(int sig)`. It uses a static `NL_TEXTMAX` buffer and delegates formatting/lookup to `__strsignal()`.

The returned pointer is to static storage unless `__strsignal()` returns a static known-signal string in non-NLS builds.
