# File Research: sources/os/bsd/freebsd-src/sbin/fdisk/Makefile

Build definition for legacy `fdisk`.

Configuration:
- `PACKAGE=runtime`
- `PROG=fdisk`
- `SRCS=fdisk.c fdisk_mbr_enc.c`
- `WARNS?=4`
- Installs `fdisk.8`
- Links `libgeom`
- Includes `<bsd.prog.mk>`

Extra target:
- `test` builds the program and runs `runtest.sh`.

Role:
- Builds the deprecated MBR partition table editor.
