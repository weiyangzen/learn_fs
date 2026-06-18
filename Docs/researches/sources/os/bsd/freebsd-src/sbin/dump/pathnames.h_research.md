# File Research: sources/os/bsd/freebsd-src/sbin/dump/pathnames.h

Defines fixed path constants for `dump`.

Constants:
- `_PATH_DEFTAPE`: default output tape device `/dev/sa0`.
- `_PATH_DUMPDATES`: default dump date database `/etc/dumpdates`.
- `_PATH_LOCK`: lock template `/tmp/dumplockXXXXXX`.
- `_PATH_RMT`: remote tape command path `/etc/rmt`.

Notes:
- Includes `<paths.h>` for common FreeBSD path constants.
- `_PATH_LOCK` is not used by the files in this group but remains part of dump path definitions.
