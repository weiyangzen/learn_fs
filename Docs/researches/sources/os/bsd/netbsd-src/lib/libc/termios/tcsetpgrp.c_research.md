# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcsetpgrp.c

## Purpose
Sets the foreground process group for a terminal.

## Key Elements
Copies `pid_t pgrp` to an `int` and calls `ioctl(fd, TIOCSPGRP, &s)`.

## Dependencies
Uses `<sys/ioctl.h>`, `<termios.h>`, and process id types.

## Behavior/Risks
Potential pid-to-int narrowing follows the historical ioctl ABI.
