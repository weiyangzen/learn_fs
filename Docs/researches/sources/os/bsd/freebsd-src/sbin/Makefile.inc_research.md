# File Research: sources/os/bsd/freebsd-src/sbin/Makefile.inc

## Purpose
Shared makefile fragment for programs under `sbin`.

## Main Elements
- Includes `src.opts.mk`.
- Defaults `BINDIR` to `/sbin`.
- Sets `NO_SHARED=YES` when `MK_DYNAMICROOT == "no"`.

## Dependencies And Integration
Consumed by descendant program makefiles through FreeBSD make include conventions. It enforces static linking behavior for non-dynamic-root builds.

## Risk Notes
Affects linkage mode broadly across `sbin`; dynamic-root option changes can alter binary dependency expectations.
