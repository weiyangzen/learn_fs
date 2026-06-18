# File Research: sources/os/bsd/freebsd-src/sbin/ccdconfig/pathnames.h

## Purpose
Defines filesystem path constants for `ccdconfig`.

## Main Elements
- `_PATH_CCDCONF`: `/etc/ccd.conf`
- `_PATH_CCDCTL`: `ccd.ctl`

## Dependencies And Integration
Included by `ccdconfig.c` for the default configuration file. `_PATH_CCDCTL` is retained as a named path constant though the modern implementation uses GEOM control APIs.
