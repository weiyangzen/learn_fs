# File Research: sources/os/bsd/freebsd-src/sbin/umount/Makefile

## Purpose
Builds the `umount` utility.

## Main Elements
- Sets `PACKAGE=runtime`, `PROG=umount`, and `MAN=umount.8`.
- Builds `umount.c`, `vfslist.c`, and `mounttab.c`.
- Adds include paths for sibling `mount` sources and `usr.sbin/rpc.umntall`.
- Uses `.PATH` to locate shared source files.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
Shares VFS list and mounttab support with related mount/rpc unmount tooling.

## Risk Notes
Build composition depends on shared source paths remaining stable.
