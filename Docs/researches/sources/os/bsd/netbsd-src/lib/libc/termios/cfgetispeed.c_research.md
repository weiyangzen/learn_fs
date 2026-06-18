# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/cfgetispeed.c

## Purpose
Returns the input baud rate from a termios structure.

## Key Elements
Asserts `t != NULL` and returns `t->c_ispeed`.

## Dependencies
Uses `<termios.h>`, `_DIAGASSERT`, and weak alias support.

## Behavior/Risks
No runtime error path for null in non-diagnostic builds; caller must provide a valid termios pointer.
