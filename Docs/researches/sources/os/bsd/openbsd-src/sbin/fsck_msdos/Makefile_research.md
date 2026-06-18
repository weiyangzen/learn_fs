# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/Makefile

## Scope

Build file for OpenBSD `fsck_msdos`.

## Build Role

- Builds `PROG=fsck_msdos` with manual page `fsck_msdos.8`.
- Sources: `main.c`, `check.c`, `boot.c`, `fat.c`, `dir.c`, plus shared `fsutil.c`.
- Adds `.PATH` to `../fsck`, includes that directory, and links `libutil`.

## Dependencies

This Makefile makes `fsck_msdos` share block-device and diagnostic support with the generic fsck code while keeping FAT-specific logic in its own directory.
