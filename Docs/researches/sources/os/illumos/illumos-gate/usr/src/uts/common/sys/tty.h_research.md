# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/tty.h

## Purpose
Common STREAMS tty state header.

## Main Interfaces
- Defines `tty_common_t` with flags, termios settings, and window size.
- Defines `TS_XCLUDE` and `TS_SOFTCAR`.
- Declares `ttycommon_close`, `ttycommon_qfull`, and `ttycommon_ioctl`.

## Dependencies And Relationships
Includes `sys/stream.h` and `sys/termios.h`. Used by STREAMS terminal drivers that share common termios/window-size handling.

## Research Notes
This is a compact helper interface for tty drivers, not a full terminal subsystem definition.
