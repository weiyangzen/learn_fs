# File Research: sources/os/bsd/freebsd-src/sbin/adjkerntz/Makefile

## Purpose
Builds the `adjkerntz` runtime utility.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=adjkerntz`.
- Installs `adjkerntz.8`.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
Relies on the default single-source FreeBSD program build rule for `adjkerntz.c`.

## Risk Notes
No special libraries or flags are specified; behavior is almost entirely in the C source.
