# File Research: sources/os/bsd/openbsd-src/sbin/dumpfs/Makefile

## Purpose
Builds `dumpfs`.

## Key Contents
- `PROG=dumpfs`
- Installs `dumpfs.8`.
- Links with `libutil`.

## Notes
`libutil` is used for OpenBSD device-opening helpers.
