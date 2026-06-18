# File Research: sources/os/bsd/freebsd-src/sbin/mount/pathnames.h

## Summary
Defines path constants used by the generic `mount` utility.

## Main Contents
- Defines `_PATH_MOUNTDPID` as `/var/run/mountd.pid`.

## Dependencies And Integration
Used by `mount.c` to signal mountd after successful root-initiated mounts.
