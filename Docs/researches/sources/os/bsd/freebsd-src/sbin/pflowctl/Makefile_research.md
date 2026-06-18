# File Research: sources/os/bsd/freebsd-src/sbin/pflowctl/Makefile

## Purpose
Builds the `pflowctl` utility.

## Main Elements
Includes `src.opts.mk`, sets `PACKAGE=pf`, `PROG=pflowctl`, `MAN=pflowctl.8`, and source `pflowctl.c`.

## Dependencies And Integration
Uses standard FreeBSD program build infrastructure.

## Risk Notes
No explicit `LIBADD` is declared here; netlink support is expected from base build context.
