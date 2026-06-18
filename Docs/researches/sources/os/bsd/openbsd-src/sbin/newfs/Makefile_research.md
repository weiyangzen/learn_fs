# File Research: sources/os/bsd/openbsd-src/sbin/newfs/Makefile

Purpose: Builds OpenBSD `newfs` and its memory filesystem alias.

Build details:
- `PROG=newfs`.
- Sources are `dkcksum.c`, `getmntopts.c`, `newfs.c`, and `mkfs.c`.
- Adds `-DMFS` and includes sibling `mount` headers for mount option handling.
- Adds `.PATH` entries for `../mount` and `../disklabel`.
- Links with `libutil`.
- Installs link `mount_mfs` pointing to the `newfs` binary.
