# File Research: sources/os/bsd/openbsd-src/sbin/ping/Makefile

## Purpose

Builds OpenBSD `ping` and links it as `ping6`.

## Build Definition

The program is `ping`, with manual page `ping.8`. It enables strict warning flags, links with `libm`, installs a hard link from `ping` to `ping6`, and installs owned by root with mode `4555`.

## Notable Detail

The same binary switches IPv4/IPv6 behavior based on the invoked program name (`ping` versus `ping6`).
