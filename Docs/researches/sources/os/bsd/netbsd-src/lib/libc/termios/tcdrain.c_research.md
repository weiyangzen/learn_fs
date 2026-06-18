# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcdrain.c

## Purpose
Waits for terminal output to drain.

## Key Elements
Calls `ioctl(fd, TIOCDRAIN, 0)`.

## Dependencies
Uses `<sys/ioctl.h>`, `<termios.h>`, and `_DIAGASSERT`.

## Behavior/Risks
All blocking and error behavior is controlled by the terminal driver.
