# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetattr.c

## Purpose
Fetches terminal attributes.

## Key Elements
Calls `ioctl(fd, TIOCGETA, t)`.

## Dependencies
Uses `<sys/ioctl.h>`, `<termios.h>`, and `_DIAGASSERT`.

## Behavior/Risks
No userland fallback; invalid fd or non-terminal handling is by ioctl.
