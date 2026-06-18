# File Research: sources/os/bsd/freebsd-src/sbin/mount_nfs/Makefile

## Summary
Builds the `mount_nfs` helper.

## Main Elements
- Sets `PACKAGE=nfs`.
- Builds `mount_nfs.c` and shared `mounttab.c`.
- Links `libutil`.
- Includes rpc.umntall source path for `mounttab` support.
- Defines `NFS`.

## Research Notes
The helper updates the traditional mounttab for non-NFSv4 mounts.
