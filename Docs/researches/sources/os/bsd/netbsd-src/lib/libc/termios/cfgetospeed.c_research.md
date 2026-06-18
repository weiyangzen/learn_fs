# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/cfgetospeed.c

## Purpose
Returns the output baud rate from a termios structure.

## Key Elements
Asserts `t != NULL` and returns `t->c_ospeed`.

## Dependencies
Uses `<termios.h>`, `_DIAGASSERT`, and weak alias support.

## Behavior/Risks
Direct structure accessor; invalid pointers are not handled beyond diagnostics.
