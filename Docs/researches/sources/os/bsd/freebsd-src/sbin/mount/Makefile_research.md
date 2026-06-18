# File Research: sources/os/bsd/freebsd-src/sbin/mount/Makefile

## Summary
Builds the generic `mount` runtime utility.

## Main Elements
- Builds `mount.c`, `mount_fs.c`, and `vfslist.c`.
- Links `libutil` and `libxo`.
- Installs `mount.8`.
- Includes `bsd.prog.mk`.

## Research Notes
`libxo` is used for structured and human-readable mount output.
