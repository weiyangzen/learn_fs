# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/gettemp.h

Internal header for the temp-name helper family. It maps `GETTEMP` either to `__nbcompat_gettemp` for nbtool builds or to libc `__gettemp`, includes the needed platform headers, and declares `int GETTEMP(char *, int *, int, int, int)`.

This header lets the same wrapper files build in both libc and host-tool compatibility contexts.
