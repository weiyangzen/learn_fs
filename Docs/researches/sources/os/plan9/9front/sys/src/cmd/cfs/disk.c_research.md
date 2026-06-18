# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/disk.c

Disk allocation and formatting layer for `cfs`.

Key behavior:
- `dinit` reads disk size, validates logical block size and allocation blocks, initializes block cache, and checks optional expected server/cache name.
- `dformat` lays out allocation bitmap blocks, writes allocation headers, records cache name, allocates allocation blocks themselves, and syncs.
- `_balloc` finds a free bit in one allocation bitmap block.
- `dalloc` scans allocation blocks to allocate one disk block and optionally initializes a `Dptr`.
- `dpalloc` allocates and initializes an indirect pointer block, marking all child pointers absent.
- `_bfree` clears an allocation bit.
- `dfree` frees direct blocks or recursively frees indirect pointer blocks and their referenced data blocks.

Dependencies:
- Includes `cformat.h`, `lru.h`, `bcache.h`, and `disk.h`.

Research notes:
- Comments warn recursive indirect freeing can fail if there are more allocation blocks than block buffers.
- Name mismatch intentionally forces cache reformat for a different remote server identity.
