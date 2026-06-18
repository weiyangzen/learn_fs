# File Research: sources/os/bsd/freebsd-src/sbin/ping/Makefile

## Purpose
Builds the setuid-root `ping`/`ping6` utility.

## Main Elements
- Sets `PACKAGE=runtime`, `PROG=ping`, `BINOWN=root`, and `BINMODE=4555`.
- Builds `main.c` always; adds IPv4 `ping.c utils.c` when `MK_INET_SUPPORT` is enabled.
- Adds IPv6 `ping6.c`, `ping6` link, and manual-page link when `MK_INET6_SUPPORT` is enabled.
- Links `m`, optional `casper`/`cap_dns`, and `ipsec`.
- Adds tests subdirectory when tests are enabled.

## Dependencies And Integration
Uses FreeBSD build options for INET, INET6, dynamic root, Casper, and IPsec.

## Risk Notes
Setuid and capability support are central to runtime security. Build options change protocol support and linked libraries.
