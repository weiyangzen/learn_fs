# File Research: sources/os/bsd/freebsd-src/sbin/tunefs/Makefile

## Purpose
Builds the UFS tuning utility `tunefs`.

## Main Elements
- Sets `PACKAGE=ufs`, `PROG=tunefs`, and `MAN=tunefs.8`.
- Links `libufs` and `libutil`.
- Enables tests under `tests` when `MK_TESTS` is enabled.
- Includes `src.opts.mk` and `bsd.prog.mk`.

## Dependencies And Integration
Depends on FreeBSD’s UFS library and test option framework.

## Risk Notes
The build file is simple; filesystem mutation behavior lives in `tunefs.c`.
