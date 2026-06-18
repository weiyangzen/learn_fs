# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/cfsetspeed.c

## Purpose
Sets both input and output baud rates in a termios structure.

## Key Elements
Assigns `t->c_ispeed = t->c_ospeed = speed` and returns `0`.

## Dependencies
Uses `<termios.h>`, `_DIAGASSERT`, and weak alias support.

## Behavior/Risks
No local rate validation; callers rely on later kernel/ioctl handling.
