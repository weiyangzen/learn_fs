# File Research: sources/os/bsd/freebsd-src/sbin/pfilctl/Makefile

## Purpose
Builds the `pfilctl` utility.

## Main Elements
Sets `PROG=pfilctl`, source `pfilctl.c`, and manual page `pfilctl.8`; includes `bsd.prog.mk`.

## Dependencies And Integration
Uses standard FreeBSD program build infrastructure.

## Risk Notes
No special libraries are declared; behavior is fully in `pfilctl.c`.
