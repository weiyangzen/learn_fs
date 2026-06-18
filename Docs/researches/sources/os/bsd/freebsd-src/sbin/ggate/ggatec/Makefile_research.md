# File Research: sources/os/bsd/freebsd-src/sbin/ggate/ggatec/Makefile

## Purpose

Builds the GEOM Gate client utility `ggatec`.

## Build Definition

- Includes parent `Makefile.inc`.
- Uses shared source path `${.CURDIR:H}/shared`.
- Program: `ggatec`
- Manual: `ggatec.8`
- Sources: `ggatec.c`, shared `ggate.c`
- Package: `ggate`
- Defines:
  - `MAX_SEND_SIZE=32768`
  - `LIBGEOM`
- Adds include path to shared ggate headers.
- Links `libgeom`, `libutil`, and pthreads.

## Integration Notes

This Makefile wires the client-specific source to the shared GEOM Gate implementation and libgeom control interface.
