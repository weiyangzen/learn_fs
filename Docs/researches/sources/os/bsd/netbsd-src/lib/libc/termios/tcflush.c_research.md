# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcflush.c

## Purpose
Flushes queued terminal input and/or output.

## Key Elements
Maps `TCIFLUSH`, `TCOFLUSH`, and `TCIOFLUSH` to `FREAD`, `FWRITE`, or both, then calls `ioctl(fd, TIOCFLUSH, &com)`.

## Dependencies
Uses `<sys/ioctl.h>`, `<fcntl.h>`, `<termios.h>`, and `errno`.

## Behavior/Risks
Invalid selector sets `EINVAL`; actual flush semantics are terminal-driver dependent.
