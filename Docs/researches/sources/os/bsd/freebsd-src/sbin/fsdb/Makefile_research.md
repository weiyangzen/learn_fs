# File Research: sources/os/bsd/freebsd-src/sbin/fsdb/Makefile

## Purpose

Builds the `fsdb` interactive UFS/FFS filesystem debugger/editor.

## Build Definition

- Program: `fsdb`
- Manual: `fsdb.8`
- Own sources: `fsdb.c`, `fsdbutil.c`
- Reuses many `fsck_ffs` sources: directory, inode, pass, setup, utility, and FFS support files.
- Includes fsck_ffs headers.
- Links `libedit` and `libufs`.
- Pulls `prtblknos.c` from diagnostic tooling.

## Integration Notes

`fsdb` is intentionally built on fsck internals so it can inspect and mutate UFS metadata through the same inode, block, and directory routines.
