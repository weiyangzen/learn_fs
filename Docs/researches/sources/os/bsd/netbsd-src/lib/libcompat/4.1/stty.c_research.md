# File Research: sources/os/bsd/netbsd-src/lib/libcompat/4.1/stty.c

## Purpose
Implements historical `stty()` compatibility API.

## Behavior
Calls `ioctl(fd, TIOCSETP, tty)` to set old `sgttyb` terminal modes.

## Dependencies
Depends on `<sgtty.h>`, ioctl definitions, and `_DIAGASSERT`.

## Risks And Notes
This is a thin wrapper around legacy terminal ioctls and inherits their behavior.
