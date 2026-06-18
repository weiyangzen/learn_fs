# File Research: sources/virtualization/nbdkit/plugins/null/null.c

## Purpose
Implements the `null` plugin: a configurable-size virtual disk that reads as zeroes and discards all writes.

## Main Entry Points
- `null_config()` parses `size=`.
- `null_get_size()` returns the configured size.
- `null_pread()` fills reads with zero bytes.
- `null_pwrite()`, `null_zero()`, `null_trim()`, and `null_flush()` are no-ops.
- Capability callbacks advertise multi-conn safety, native cache no-op, fast zero, and native FUA.
- `null_extents()` reports the whole disk as a zero hole.

## Dependencies
Uses nbdkit plugin API v2 and standard C `memset`.

## Risks and Notes
The plugin has no `config_complete()` check that `size=` was supplied, so the default disk size is zero. Extents always report from offset `0` to `size`, independent of the requested range; this matches a simple whole-disk model but relies on nbdkit accepting broad extents.
