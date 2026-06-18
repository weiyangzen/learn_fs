# File Research: sources/os/bsd/freebsd-src/sbin/ping/main.h

## Purpose
Shared declarations and option strings for ping IPv4/IPv6 implementations.

## Main Elements
- Defines `PING4OPTS` and `PING6OPTS`, including conditional IPsec option characters.
- Declares shared option flag `F_HOSTNAME`.
- Declares global hostname, counters, signal flags, and timing accumulators.
- Declares `onsignal()`, `pr_summary()`, and `usage()`.

## Dependencies And Integration
Included by `main.c`, `ping.c`, and IPv6 implementation files.

## Risk Notes
Option strings must stay synchronized with actual parser switch cases.
