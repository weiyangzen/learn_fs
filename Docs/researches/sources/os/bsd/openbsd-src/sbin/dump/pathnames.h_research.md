# File Research: sources/os/bsd/openbsd-src/sbin/dump/pathnames.h

## Purpose
Path constants for `dump`.

## Key Contents
- `_PATH_DUMPDATES` as `/etc/dumpdates`.
- `_PATH_LOCK` as `/tmp/dumplockXXXXXX`.
- `_PATH_RMT` as `/etc/rmt`.
- `_PATH_WALL` as `/usr/bin/wall`.

## Notes
The lock path is declared here even though this grouped subset’s read code primarily uses file locking on dumpdates.
