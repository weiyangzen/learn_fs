# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcsetwinsize.c

## Purpose
Sets terminal window size.

## Key Elements
Ensures `_NETBSD_SOURCE` for ioctl constants and calls `ioctl(fd, TIOCSWINSZ, ws)`.

## Dependencies
Uses `<sys/ioctl.h>` and `<termios.h>`.

## Behavior/Risks
Thin ioctl wrapper; signal generation and validation are terminal-driver responsibilities.
