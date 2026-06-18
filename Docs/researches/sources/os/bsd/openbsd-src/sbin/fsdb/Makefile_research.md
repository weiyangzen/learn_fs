# File Research: sources/os/bsd/openbsd-src/sbin/fsdb/Makefile

## Scope

Build file for OpenBSD `fsdb`, the interactive FFS filesystem debugger.

## Build Role

- Builds `PROG=fsdb` with manual page `fsdb.8`.
- Local sources: `fsdb.c`, `fsdbutil.c`.
- Reuses many modules from `../../sbin/fsck` and `../../sbin/fsck_ffs`, including directory, inode, pass, setup, utility, and FFS subr/table code.
- Includes fsck and fsck_ffs headers, links `libedit`, `libcurses`, and `libutil`.

## Dependencies

The Makefile intentionally composes `fsdb` from fsck internals so the debugger can use the same inode/block access and mutation logic as `fsck_ffs`.
