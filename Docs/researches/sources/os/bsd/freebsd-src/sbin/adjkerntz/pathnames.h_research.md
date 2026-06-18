# File Research: sources/os/bsd/freebsd-src/sbin/adjkerntz/pathnames.h

## Purpose
Defines path constants for `adjkerntz`.

## Main Elements
- Includes `<paths.h>`.
- Defines `_PATH_CLOCK` as `/etc/wall_cmos_clock`.

## Dependencies And Integration
`adjkerntz.c` uses `_PATH_CLOCK` as the marker file that enables wall CMOS clock behavior.

## Risk Notes
Changing this path changes system policy detection for local-time RTC handling.
