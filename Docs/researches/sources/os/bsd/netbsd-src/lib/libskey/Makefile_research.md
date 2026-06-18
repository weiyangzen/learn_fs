# File Research: sources/os/bsd/netbsd-src/lib/libskey/Makefile

## Purpose
Builds the S/Key one-time-password library.

## Key Elements
Defines `LIB=skey`, source files `skeylogin.c skeysubr.c put.c`, installs `skey.h` to `/usr/include`, enables fortified authentication build defaults via `USE_FORT?=yes`, and installs `skey.3` with MLINK aliases for the public APIs.

## Dependencies
Uses NetBSD `bsd.lib.mk` and the local S/Key implementation files.

## Risks And Notes
The public API surface is driven by the installed header and manpage aliases. Hash and database behavior lives in the C sources, not the makefile.
