# File Research: sources/os/bsd/freebsd-src/sbin/kldunload/Makefile

## Purpose
Builds the `kldunload` runtime utility.

## Main Responsibilities
- Sets `PACKAGE=runtime`.
- Builds `PROG=kldunload`.
- Installs `kldunload.8`.
- Includes `bsd.prog.mk`.
