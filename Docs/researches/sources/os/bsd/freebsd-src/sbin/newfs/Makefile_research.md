# File Research: sources/os/bsd/freebsd-src/sbin/newfs/Makefile

## Summary
Builds the UFS `newfs` utility and defines legacy test targets.

## Main Elements
- Adds `.PATH: ${SRCTOP}/sys/geom` to build `geom_bsd_enc.c`.
- Sets `PACKAGE=ufs`.
- Builds `PROG=newfs`.
- Sources: `newfs.c`, `mkfs.c`, and `geom_bsd_enc.c`.
- Links `libufs` and `libutil`.
- Installs `newfs.8`.
- Defines a manual `test` target that runs `runtest01.sh`, `runtest00.sh`, compares against `ref.test`, and prints success.

## Research Notes
This Makefile is the build glue for the UFS filesystem creation tool; the implementation files are outside this grouped batch.
