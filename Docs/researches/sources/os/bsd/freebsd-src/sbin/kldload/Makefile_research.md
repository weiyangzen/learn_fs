# File Research: sources/os/bsd/freebsd-src/sbin/kldload/Makefile

## Purpose
Builds the `kldload` runtime utility.

## Main Responsibilities
- Sets `PACKAGE=runtime`.
- Builds `PROG=kldload`.
- Installs `kldload.8`.
- Includes `bsd.prog.mk`.
