# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcgetpgrp.c

## Purpose
Gets the foreground process group for a terminal.

## Key Elements
Calls `ioctl(fd, TIOCGPGRP, &s)`, returns `-1` on ioctl failure, and maps a returned `-1` process group to a large invalid positive value for SVID compatibility.

## Dependencies
Uses `<sys/ioctl.h>`, `<termios.h>`, and process id types.

## Behavior/Risks
The special SVID mapping is intentional and could surprise code expecting the raw kernel value.
