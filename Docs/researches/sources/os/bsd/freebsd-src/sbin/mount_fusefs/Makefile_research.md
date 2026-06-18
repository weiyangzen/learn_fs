# File Research: sources/os/bsd/freebsd-src/sbin/mount_fusefs/Makefile

## Summary
Builds the `mount_fusefs` helper with optional debug compile flags.

## Main Elements
- Supports `DEBUG`, `DEBUG2G`, `DEBUG3G`, `DEBUG_MSG`, and `F4BVERS` make-time flags.
- Builds `PROG=mount_fusefs`.
- Links `libutil`.
- Installs `mount_fusefs.8`.

## Research Notes
The Makefile preserves legacy fuse4bsd version/debug controls.
