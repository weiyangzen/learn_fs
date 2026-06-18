# File Research: sources/os/bsd/netbsd-src/lib/libc_fp/Makefile

## Purpose
Builds `libc_fp`, an architecture-selected floating-point support library.

## Build Behavior
Includes the first matching architecture `Makefile.inc` from CPU, architecture, or machine directories and builds `LIB=c_fp` only when sources are selected.

## Dependencies
Depends on NetBSD make architecture variables and `bsd.lib.mk`.

## Risks And Notes
This generic makefile contains no FP code itself; source selection is entirely architecture-driven.
