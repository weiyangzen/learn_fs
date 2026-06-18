# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ttcompat.h

## Purpose
State definitions for the STREAMS terminal compatibility module handling old tty ioctls.

## Main Interfaces
- Defines compatibility message/state structures holding old and new tty settings, ioctl state, and transparent ioctl bookkeeping.
- Uses legacy tty structures such as `sgttyb`, `tchars`, and `ltchars`.
- Defines state flags `TS_FREE`, `TS_INUSE`, `TS_W_IN`, `TS_W_OUT`, `TS_IOCWAIT`, and `TS_TIOCNAK`.

## Dependencies And Relationships
Works with old tty definitions in `ttold.h` and modern STREAMS/termios code. It supports conversion between legacy BSD/SVr3 terminal ioctls and current terminal behavior.

## Research Notes
This header is compatibility plumbing. The state flags reflect multi-step STREAMS ioctl translation rather than direct device operation.
