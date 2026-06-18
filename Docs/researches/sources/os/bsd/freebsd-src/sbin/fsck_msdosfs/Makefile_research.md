# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/Makefile

## Purpose

Builds the `fsck_msdosfs` FAT filesystem checker.

## Build Definition

- Program: `fsck_msdosfs`
- Manual page: `fsck_msdosfs.8`
- Sources: `main.c`, `check.c`, `boot.c`, `fat.c`, `dir.c`, and shared `fsutil.c`
- Adds include path to sibling `fsck`
- Defines `HAVE_LIBUTIL_H`
- Links `libutil`

## Integration Notes

Uses `.PATH` to pull `fsutil.c` from `sbin/fsck`, sharing prompting and diagnostic helpers with other fsck utilities.
