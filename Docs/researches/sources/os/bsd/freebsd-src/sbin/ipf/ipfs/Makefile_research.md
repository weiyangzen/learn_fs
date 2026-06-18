# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfs/Makefile

## Purpose
Builds the `ipfs` utility.

## Main Elements
- Sets `PACKAGE=ipf`.
- Builds `PROG=ipfs`.
- Installs `ipfs.8`.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
Relies on default single-source program rules for `ipfs.c` plus shared IPFilter make settings from parent includes.

## Risk Notes
No special libraries or sources are declared here; behavior is concentrated in `ipfs.c`.
