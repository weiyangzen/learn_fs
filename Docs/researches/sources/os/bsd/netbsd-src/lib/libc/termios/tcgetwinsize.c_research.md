# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetwinsize.c

## Purpose
Gets terminal window size.

## Key Elements
Ensures `_NETBSD_SOURCE` so ioctl constants are visible through headers, then calls `ioctl(fd, TIOCGWINSZ, ws)`.

## Dependencies
Uses `<sys/ioctl.h>` and `<termios.h>`.

## Behavior/Risks
Thin ioctl wrapper; no local pointer or fd checks.
