# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/initparse.c

This file defines global `thishost` and initializes it for parser use.

`initparse()` calls `gethostname()` into `thishost` and guarantees NUL termination. Helpers such as `gethost()` use `thishost` to resolve the special token `<thishost>`.
