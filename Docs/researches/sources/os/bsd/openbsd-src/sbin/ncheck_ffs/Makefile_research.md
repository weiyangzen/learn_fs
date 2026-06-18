# File Research: sources/os/bsd/openbsd-src/sbin/ncheck_ffs/Makefile

Purpose: Builds the `ncheck_ffs` utility.

Build details:
- `PROG=ncheck_ffs`.
- Links with `libutil` through `DPADD+=${LIBUTIL}` and `LDADD+=-lutil`.
- Installs manual page `ncheck_ffs.8`.
- Adds compatibility link from `ncheck_ffs` to `ncheck`.
- Uses standard OpenBSD `<bsd.prog.mk>`.
