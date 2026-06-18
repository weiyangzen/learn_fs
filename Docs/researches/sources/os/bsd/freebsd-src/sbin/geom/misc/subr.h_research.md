# File Research: sources/os/bsd/freebsd-src/sbin/geom/misc/subr.h

## Purpose

Header for shared GEOM helper routines implemented in `subr.c`.

## Contents

Declares:
- `g_lcm()`
- `bitcount32()`
- `g_parse_lba()`
- `g_get_mediasize()`
- `g_get_sectorsize()`
- Metadata read/store/clear helpers
- `gctl_req` error, getter, mutator, deletion, and existence helpers

## Integration Notes

Included by `geom/core/geom.c` and GEOM class tools that need consistent metadata and argument handling.
