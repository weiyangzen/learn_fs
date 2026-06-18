# File Research: sources/os/bsd/openbsd-src/sbin/mount/pathnames.h

`pathnames.h` defines path constants used by the generic `mount` command: `/sbin`, `/usr/sbin`, and `/var/run/mountd.pid`.

These paths control where `mount` searches for filesystem helpers and where it finds `mountd` for post-mount SIGHUP notification.
