# File Research: sources/os/bsd/openbsd-src/sbin/pflogd/Makefile

## Purpose

Builds the `pflogd` daemon.

## Build Definition

The program is `pflogd`, with sources `pflogd.c`, `privsep.c`, and `privsep_fdpass.c`, and manual page `pflogd.8`. It adds strict warning flags, includes `../../lib/libpcap` for `pcap-int.h`, and links against `libpcap`.

## Notable Detail

`LDSTATIC=` is explicitly cleared so `pflogd` is not built as a static binary by default.
