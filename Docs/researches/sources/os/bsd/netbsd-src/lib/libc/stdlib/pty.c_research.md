# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/pty.c

Implements POSIX pty helper functions. `grantpt()` issues `TIOCGRANTPT`, `unlockpt()` is a no-op returning success, and `ptsname()`/`ptsname_r()` query `TIOCPTSNAME` into `struct ptmget`.

`ptsname()` returns a static buffer and is not thread-safe. `ptsname_r()` validates `buf`, returns ioctl `errno` values directly, and reports `ERANGE` if the slave path does not fit.
