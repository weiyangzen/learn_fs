# File Research: sources/virtualization/nbdkit/plugins/pattern/pattern.c

## Purpose
Implements the `pattern` plugin, a deterministic read-only-style test disk whose contents encode offsets in repeated big-endian 64-bit words.

## Main Entry Points
- `pattern_load()` seeds random state for `upper=random`.
- `pattern_config()` parses `size=`, `stride=`, and `upper=`.
- `pattern_get_size()` returns the configured size.
- `pattern_pread()` generates expected data for each requested offset/stride.
- `pattern_pwrite()` verifies that written data exactly matches what `pattern_pread()` would produce.
- Capability callbacks advertise multi-conn safety and native cache no-op.

## Internal Mechanics
For each stride-sized block, the first 8 bytes contain `htobe64(upper ^ offset)`. If `stride > 8`, bytes after the first 8 in each stride are zero. The fast path handles aligned requests; the slow path handles unaligned reads crossing stride boundaries.

## Dependencies
Uses nbdkit parsing APIs, byte swapping, alignment/power-of-two helpers, random helpers, cleanup allocation, and standard memory operations.

## Risks and Notes
The plugin does not implement writes as state changes; writes are validation only and return EIO if the client writes unexpected bytes. `upper=random` chooses a nonzero 16-bit prefix at configuration time, making contents intentionally nondeterministic across runs.
