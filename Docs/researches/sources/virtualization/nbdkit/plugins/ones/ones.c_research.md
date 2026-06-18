# File Research: sources/virtualization/nbdkit/plugins/ones/ones.c

## Purpose
Implements the `ones` plugin: a configurable-size virtual disk that reads as a repeating byte, defaulting to `0xff`, and discards writes.

## Main Entry Points
- `ones_config()` parses `size=` and `byte=`.
- `ones_get_size()` returns the configured size.
- `ones_pread()` fills reads with the configured byte.
- `ones_pwrite()`, `ones_zero()`, `ones_trim()`, and `ones_flush()` are no-ops.
- Capability callbacks advertise multi-conn safety, native cache no-op, fast zero, and native FUA.
- `ones_extents()` reports the whole disk as allocated data.

## Dependencies
Uses nbdkit plugin API v2 and standard C memory operations.

## Risks and Notes
As with `null`, absent `size=` leaves a zero-sized disk. The plugin advertises fast zero even though reads still return the configured byte; zero/write/trim are discard operations, so clients must not expect writes to change subsequent reads.
