# File Research: sources/os/bsd/freebsd-src/sbin/zfsbootcfg/Makefile

## Purpose
Builds the `zfsbootcfg` utility.

## Main Elements
- Sets `PACKAGE=zfs`, `PROG=zfsbootcfg`, and `MAN=zfsbootcfg.8`.
- Links `libzfsbootenv`.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
Part of FreeBSD’s ZFS package utilities.

## Risk Notes
Build depends on libzfsbootenv availability.
