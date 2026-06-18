# File Research: sources/os/bsd/netbsd-src/lib/libc/yp/Makefile.inc

## Purpose
Adds Yellow Pages/NIS client support sources and manpage links to libc.

## Build Behavior
Extends `.PATH` with architecture-specific and generic `yp` directories, adds XDR helpers, binding logic, client procedures, and error conversion sources to `SRCS`, and installs `ypclnt.3` links for the exported YP client APIs.

## Dependencies
Relies on NetBSD libc make infrastructure and RPC/YP headers from the source tree.

## Risks And Notes
This file defines the set of libc YP entry points compiled into libc; actual behavior is in the listed C files.
