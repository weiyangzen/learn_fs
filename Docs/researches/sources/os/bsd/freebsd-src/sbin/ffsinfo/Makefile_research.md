# File Research: sources/os/bsd/freebsd-src/sbin/ffsinfo/Makefile

Build definition for `ffsinfo`.

Configuration:
- Reuses growfs debug support through:
  - `GROWFS= ${.CURDIR:H}/growfs`
  - `.PATH: ${GROWFS}`
- `PACKAGE=ufs`
- `PROG=ffsinfo`
- `SRCS=ffsinfo.c debug.c`
- Installs `ffsinfo.8`
- `WARNS?=1`
- Adds `-DFS_DEBUG -I${GROWFS}`
- Links `libufs`
- Includes `<bsd.prog.mk>`

Role:
- Builds a detailed UFS metadata dump tool using shared debug dumping routines from `growfs`.
