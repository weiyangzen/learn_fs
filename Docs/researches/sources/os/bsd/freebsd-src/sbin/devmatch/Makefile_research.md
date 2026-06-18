# File Research: sources/os/bsd/freebsd-src/sbin/devmatch/Makefile

## Purpose
Builds the `devmatch` utility.

## Main Elements
- `PACKAGE=devmatch`
- `PROG=devmatch`
- `MAN=devmatch.8`
- `LIBADD=devinfo`
- Includes `<bsd.prog.mk>`.

## Dependencies And Integration
Links `libdevinfo` to inspect the device tree.
