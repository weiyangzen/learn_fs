# File Research: sources/os/bsd/freebsd-src/sbin/ccdconfig/Makefile

## Purpose
Builds the `ccdconfig` utility.

## Main Elements
- `PACKAGE=ccdconfig`
- `PROG=ccdconfig`
- `MAN=ccdconfig.8`
- `LIBADD=geom`
- Includes `<bsd.prog.mk>`.

## Dependencies And Integration
Links against `libgeom` because the utility controls CCD GEOM instances through GEOM control requests.
