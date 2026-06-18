# File Research: sources/os/bsd/freebsd-src/sbin/dumpfs/Makefile

Build definition for `dumpfs`.

Configuration:
- `PACKAGE=ufs`
- `PROG=dumpfs`
- `WARNS?=2`
- Links `libufs` through `LIBADD=ufs`
- Installs `dumpfs.8`
- Includes `<bsd.prog.mk>`

Role:
- Builds the UFS filesystem inspection utility implemented by `dumpfs.c`.
