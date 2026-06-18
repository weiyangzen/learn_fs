# File Research: sources/os/bsd/openbsd-src/sbin/vnconfig/Makefile

Builds the `vnconfig` program.

Key contents:
- `PROG=vnconfig`
- Links against `libutil` through `LDADD=-lutil` and `DPADD=${LIBUTIL}`.
- Enables `-Wall` diagnostics through `CDIAGFLAGS`.
- Installs `vnconfig.8`.
- Includes OpenBSD `bsd.prog.mk`.

Filesystem/OS relevance:
- `vnconfig` is a block-device configuration utility for vnode-backed disk images.
