# File Research: sources/os/bsd/netbsd-src/lib/libc/nls/Makefile.inc

Build include for libc native language support catalog routines. It adds the `nls` directory to `.PATH`, builds `catclose.c`, `catgets.c`, and `catopen.c`, and installs their manual pages.

`catopen.c` receives an extra include path for libc citrus headers.
