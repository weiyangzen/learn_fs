# File Research: sources/os/bsd/netbsd-src/lib/libwrap/Makefile

## Purpose
Build definition for NetBSD `libwrap`, the TCP wrappers access-control library.

## Key Details
- Builds `LIB=wrap`.
- Enables fortification by default for network server use.
- Source list includes access matching, option processing, shell command helpers, RFC931 lookup, socket helpers, diagnostics, and `%m` expansion.
- Installs `tcpd.h`.
- Links against `libblocklist`.

## Dependencies and Role
- Network access-control library build index.
