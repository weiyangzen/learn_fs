# File Research: sources/os/bsd/freebsd-src/sbin/clri/Makefile

## Purpose
Builds the `clri` UFS inode-clearing utility.

## Main Elements
- `PACKAGE=ufs`
- `PROG=clri`
- `MAN=clri.8`
- `LIBADD=ufs`
- `WARNS?=2`
- Includes `<bsd.prog.mk>`.

## Dependencies And Integration
Links `libufs` for superblock and inode access.
