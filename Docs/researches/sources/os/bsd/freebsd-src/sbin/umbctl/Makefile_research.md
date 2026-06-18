# File Research: sources/os/bsd/freebsd-src/sbin/umbctl/Makefile

## Purpose
Builds the `umbctl` utility for controlling USB MBIM network interfaces.

## Main Elements
- Adds include path `${SRCTOP}/sys/dev/usb/net`.
- Sets `PROG=umbctl`, `MAN=umbctl.8`, and `BINDIR=/sbin`.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
Depends on MBIM and UMB driver headers under the kernel USB network tree.

## Risk Notes
Build depends on in-tree kernel header layout.
