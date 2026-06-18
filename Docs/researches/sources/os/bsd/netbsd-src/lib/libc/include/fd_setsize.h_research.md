# File Research: sources/os/bsd/netbsd-src/lib/libc/include/fd_setsize.h

Minimal compatibility header for BIND/ISC ports.

It only defines the include guard `_FD_SETSIZE_H` and comments that this is not where callers should increase `FD_SETSIZE`; it is a fallback when BIND ports do not specify their own.
