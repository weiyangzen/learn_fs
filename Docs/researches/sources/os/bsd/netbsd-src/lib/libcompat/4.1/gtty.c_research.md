# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.1/gtty.c

## Purpose
Implements historical `gtty()` compatibility API.

## Behavior
Calls `ioctl(fd, TIOCGETP, tty)` to fetch old `sgttyb` terminal modes.

## Dependencies
Depends on `<sgtty.h>`, ioctl definitions, and `_DIAGASSERT`.

## Risks And Notes
This is a thin wrapper around legacy terminal ioctls.
