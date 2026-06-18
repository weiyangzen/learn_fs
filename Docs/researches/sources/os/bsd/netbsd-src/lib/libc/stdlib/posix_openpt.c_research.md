# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/posix_openpt.c

Implements `posix_openpt(int oflag)` as a direct `open("/dev/ptmx", oflag)` wrapper. All pty allocation semantics are delegated to the kernel device.

There is no flag filtering or fallback logic in this file.
