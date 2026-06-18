# File Research: sources/os/bsd/freebsd-src/sbin/mksnap_ffs/Makefile

## Summary
Builds the `mksnap_ffs` UFS snapshot utility.

## Main Elements
- Sets `.PATH` to reuse mount support context.
- Sets `PACKAGE=ufs`.
- Builds `PROG=mksnap_ffs`.
- Links `libutil`.
- Installs `mksnap_ffs.8`.
- Uses setuid-root/operator-group install mode unless `NOSUID` is defined.
- Includes `bsd.prog.mk`.

## Research Notes
The install mode and operator group are part of the utility’s permission model for creating filesystem snapshots.
