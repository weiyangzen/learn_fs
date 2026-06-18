# File Research: sources/os/bsd/freebsd-src/sbin/dmesg/Makefile

## Purpose
Build definition for the FreeBSD `dmesg` utility.

## Main Elements
- Sets package to `runtime`.
- Builds program `dmesg`.
- Installs `dmesg.8`.
- Links `libkvm`.
- Includes `bsd.prog.mk`.

## Dependencies And Integration
Part of the FreeBSD base-system build. `libkvm` supports reading message buffers from kernel crash/core files.

## Risk Notes
No conditional logic; maintenance risk is limited to keeping libraries and manpage aligned with `dmesg.c`.
