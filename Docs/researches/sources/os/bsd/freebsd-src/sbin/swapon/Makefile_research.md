# File Research: sources/os/bsd/freebsd-src/sbin/swapon/Makefile

## Summary
Builds the `swapon` runtime utility and installs `swapoff` and `swapctl` aliases.

## Main Elements
- Sets `PACKAGE=runtime`.
- Builds `PROG=swapon` and `swapon.8`.
- Adds links for `swapoff` and `swapctl`.
- Adds manual aliases for `swapoff.8` and `swapctl.8`.
- Links `libutil`.
- Enables the `tests` subdirectory when `MK_TESTS` is on.

## Dependencies And Integration
Uses FreeBSD `bsd.prog.mk`, `src.opts.mk`, and libutil.
