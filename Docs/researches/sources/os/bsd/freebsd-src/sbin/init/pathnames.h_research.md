# File Research: sources/os/bsd/freebsd-src/sbin/init/pathnames.h

## Purpose
Defines fixed path constants used by `init(8)`.

## Main Elements
- Includes `<paths.h>`.
- Defines `_PATH_INITLOG`, `_PATH_SLOGGER`, `_PATH_RUNCOM`, `_PATH_RUNDOWN`, `_PATH_RUNFINAL`, `_PATH_REROOT`, and `_PATH_REROOT_INIT`.

## Dependencies And Integration
Consumed by `init.c` for fallback logging, startup and shutdown scripts, final shutdown script, and the temporary reroot init location.

## Risk Notes
Changing these paths changes boot, shutdown, and reroot behavior system-wide.
