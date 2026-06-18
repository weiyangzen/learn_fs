# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/cfmakeraw.c

## Purpose
Transforms an existing termios structure to raw mode.

## Key Elements
Clears input translation/break/strip/flow flags, disables output postprocessing, disables echo/canonical/signals/extensions, clears size/parity bits, and sets `CS8`.

## Dependencies
Uses `<termios.h>`, `_DIAGASSERT`, and weak alias support.

## Behavior/Risks
The file notes `MIN/TIME` are not set. It mutates the caller's structure in place and performs no validity checking beyond diagnostics.
