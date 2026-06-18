# File Research: sources/os/bsd/freebsd-src/sbin/pflogd/Makefile

## Purpose
Builds `pflogd` from contributed PF logging daemon sources.

## Main Elements
- Sets `.PATH` to `${SRCTOP}/contrib/pf/pflogd`.
- Builds `pflogd.c`, `pidfile.c`, `privsep.c`, and `privsep_fdpass.c`.
- Includes libpcap config/header paths.
- Links against `pcap`.
- Sets `PACKAGE=pf` and `WARNS?=2`.

## Dependencies And Integration
Uses contributed PF pflogd source and in-tree libpcap configuration.

## Risk Notes
Build correctness depends on contrib path and libpcap include configuration.
