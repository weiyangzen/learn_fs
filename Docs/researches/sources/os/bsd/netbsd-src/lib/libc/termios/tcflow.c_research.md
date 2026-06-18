# File Research: sources/os/bsd/netbsd-src/lib/libc/termios/tcflow.c

## Purpose
Controls terminal input/output flow.

## Key Elements
Maps `TCOOFF`/`TCOON` to `TIOCSTOP`/`TIOCSTART`. For `TCION`/`TCIOFF`, fetches termios, selects `VSTART` or `VSTOP`, and writes that control byte if not disabled.

## Dependencies
Uses `ioctl`, `tcgetattr`, `write`, `<termios.h>`, and `errno`.

## Behavior/Risks
Invalid actions set `EINVAL`. Software flow-control writes can fail independently after successful attribute lookup.
