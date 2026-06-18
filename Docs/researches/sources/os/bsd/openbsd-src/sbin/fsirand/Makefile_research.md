# File Research: sources/os/bsd/openbsd-src/sbin/fsirand/Makefile

## Scope

Build file for OpenBSD `fsirand`.

## Build Role

- Builds `PROG=fsirand` with manual page `fsirand.8`.
- Links `libutil`.

## Dependencies

The program itself is a single-source utility using OpenBSD device helpers from `libutil`.
