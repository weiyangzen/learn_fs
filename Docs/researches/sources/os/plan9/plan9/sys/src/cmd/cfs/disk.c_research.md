# File Research: sources/os/plan9/plan9/sys/src/cmd/cfs/disk.c

This file manages allocation blocks and disk-level cache formatting for `cfs`.

Key behavior:
- `dinit()` reads and validates the cache partition’s allocation metadata, logical block size, allocation block count, and cache name.
- `dformat()` initializes allocation blocks and reserves the allocation blocks themselves.
- `_balloc()` finds and sets a free bit in an allocation bitmap.
- `dalloc()` allocates a data block and optionally initializes a `Dptr`.
- `dpalloc()` allocates and initializes an indirect pointer block.
- `_bfree()` clears an allocation bit.
- `dfree()` frees direct or recursively indirect data blocks.

Important details:
- Logical block size must be a multiple of the physical sector size.
- Name mismatch causes initialization failure so callers can reformat for a different server.
- `dfree()` notes a risk if recursive indirect freeing needs more allocation blocks than cache buffers.

Filesystem relevance:
- Direct. Provides free-space management for the `cfs` persistent cache.
