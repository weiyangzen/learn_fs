# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/cfsetispeed.c

## Purpose
Sets the input baud rate in a termios structure.

## Key Elements
Assigns `t->c_ispeed = speed` and returns `0`.

## Dependencies
Uses `<termios.h>`, `_DIAGASSERT`, and weak alias support.

## Behavior/Risks
Does not validate `speed`; validation is deferred to later terminal attribute application.
