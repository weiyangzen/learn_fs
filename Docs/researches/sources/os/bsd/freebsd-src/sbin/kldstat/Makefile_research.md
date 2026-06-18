# File Research: sources/os/bsd/freebsd-src/sbin/kldstat/Makefile

## Purpose
Builds the `kldstat` runtime utility.

## Main Responsibilities
- Sets `PACKAGE=runtime`.
- Builds `PROG=kldstat`.
- Installs `kldstat.8`.
- Links against `libutil`.
- Includes `bsd.prog.mk`.
