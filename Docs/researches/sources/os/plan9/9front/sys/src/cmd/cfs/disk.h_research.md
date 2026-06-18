# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/disk.h

Disk allocator structure and declarations for `cfs`.

Key definitions:
- `Disk` embeds `Bcache` and stores total block count, allocation-block count, bitmap capacity per allocation block, pointers per indirect block, and cache name.
- Declares `dinit`, `dformat`, `dalloc`, `dpalloc`, and `dfree`.
- Defines `DPRINT` debug-print macro gated by global `debug`.

Dependencies:
- Requires `Bcache` and on-disk format types.

Research notes:
- `Disk` is intentionally a subtype-like extension of `Bcache`.
