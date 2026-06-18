# File Research: sources/os/bsd/freebsd-src/sbin/natd/Makefile

## Summary
Builds the `natd` daemon.

## Main Elements
- Sets `PACKAGE=natd`.
- Builds `natd.c` and `icmp.c`.
- Links `libalias`.
- Installs `natd.8`.
- Sets `WARNS?=3`.
