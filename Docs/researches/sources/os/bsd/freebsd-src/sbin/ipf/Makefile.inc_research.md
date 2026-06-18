# File Research: sources/os/bsd/freebsd-src/sbin/ipf/Makefile.inc

## Purpose
Shared makefile fragment for IPFilter programs.

## Main Elements
- Sets warning level and disables format-warning promotion.
- Adds include paths for kernel headers, IPFilter kernel headers, and common IPF userland headers.
- Defines `STATETOP` and `__UIO_EXPOSE`.
- Defines `USE_INET6` or `NOINET6` based on `MK_INET6_SUPPORT`.
- Links non-`libipf` programs with `libipf`.
- Adds yacc-generated cleanup files and shared `.PATH` entries.
- Includes parent `../Makefile.inc`.

## Dependencies And Integration
Centralizes common compiler flags and generated-file cleanup for `sbin/ipf` subprograms.

## Risk Notes
The IPv6 build knob changes parser and address-handling behavior across the whole IPFilter toolset.
