# File Research: sources/os/bsd/freebsd-src/sbin/geom/misc/subr.c

## Purpose

Shared GEOM helper routines for numeric parsing, provider metadata I/O, media queries, bit math, and `gctl_req` parameter manipulation.

## Main Functions

- Math:
  - `g_lcm()`
  - `bitcount32()`
- User size/LBA parsing:
  - `g_parse_lba()`: parses sector/byte values with suffixes `k/m/g/t/p/e`, `b`, and `s`, returning sector counts.
- Provider queries:
  - `g_get_mediasize()`
  - `g_get_sectorsize()`
- Metadata:
  - `g_metadata_read()`: reads last sector, optionally validates magic.
  - `g_metadata_store()`: writes metadata at last sector and flushes.
  - `g_metadata_clear()`: zeros last sector, optionally only if magic matches.
- `gctl` helpers:
  - `gctl_error()`
  - `gctl_get_int()`
  - `gctl_get_intmax()`
  - `gctl_get_ascii()`
  - `gctl_change_param()`
  - `gctl_delete_param()`
  - `gctl_has_param()`

## Metadata Format

`std_metadata_decode()` decodes a standard metadata prefix:
- 16-byte magic
- little-endian 32-bit version

## Integration Points

Used by GEOM class utilities and `geom.c`. Relies on `libgeom` provider open/close/media APIs and `gctl_req` internals.

## Risk Notes

Metadata routines assert metadata fits in one sector. `gctl_get_param()` aborts on missing, unterminated, or wrong-length params, making these helpers suitable for programmer errors rather than user-facing optional lookups.
