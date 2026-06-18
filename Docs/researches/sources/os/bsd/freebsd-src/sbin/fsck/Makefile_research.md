# File Research: sources/os/bsd/freebsd-src/sbin/fsck/Makefile

Build definition for generic `fsck` dispatcher.

Configuration:
- `PACKAGE=runtime`
- `PROG=fsck`
- `SRCS=fsck.c fsutil.c preen.c`
- Installs `fsck.8`
- Links `libutil`
- Includes `<bsd.prog.mk>`

Role:
- Builds the filesystem-check dispatcher that invokes filesystem-specific `fsck_<type>` helpers.
