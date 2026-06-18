# File Research: sources/os/bsd/netbsd-src/lib/libc/uuid/Makefile.inc

## Purpose
Adds the DCE 1.1 compatible UUID implementation to libc.

## Build Behavior
Extends `.PATH` to `${.CURDIR}/uuid`, adds comparison, creation, nil, equality, parse, hash, nil-test, stream encode/decode, and string conversion sources to `SRCS`, and installs `uuid.3` with manual-page links for all UUID APIs.

## Dependencies
Uses the parent libc build system and the public `uuid.3` manual page as the central documentation target.

## Risks And Notes
This file is build metadata only; it defines the public API surface by listing sources and MLINKS.
