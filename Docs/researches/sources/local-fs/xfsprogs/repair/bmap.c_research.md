# File Research: sources/local-fs/xfsprogs/repair/bmap.c

## Purpose

`bmap.c` implements a simple repair-local logical-to-physical block map for inode forks. It stores sorted extent records in a dynamically sized array and uses thread-local storage to reuse one data-fork and one attr-fork map per worker thread.

## Main Operations

- `blkmap_alloc` obtains or grows a thread-local map for a fork and resets `nexts`.
- `blkmap_free` releases unusually large maps to avoid pinning memory after pathological files.
- `blkmap_free_final` frees both thread-local maps at thread shutdown.
- `blkmap_set_ext` inserts an extent sorted by logical offset.
- `blkmap_get` maps one logical block to a filesystem block.
- `blkmap_getn` maps a multi-block logical range, optimized for single-extent directory/attr block reads.
- `blkmap_last_off` returns the logical offset just past the last extent.
- `blkmap_next_off` iterates mapped logical offsets while tracking an extent index.

## Data Model

`blkmap_t` contains:

- `naexts`: allocated extent capacity.
- `nexts`: number of active extents.
- `exts[]`: flexible extent array.

Each `bmap_ext_t` records logical start offset, physical filesystem block, and block count.

## Memory and Capacity Handling

The implementation caps allocation at `XFS_MAX_EXTCNT_DATA_FORK_LARGE` and has explicit 32-bit overflow checks around `BLKMAP_SIZE`. `blkmap_grow` grows in small increments for small files and larger increments for fragmented files.

## Important Invariants

- Extents are stored in increasing `startoff` order.
- `blkmap_get` returns `NULLFSBLOCK` if no mapping contains the requested offset.
- `blkmap_set_ext` leaves the caller’s map pointer unchanged on allocation failure.
- Thread-local keys distinguish data fork and attr fork maps.
- `blkmap_getn` may allocate a temporary extent list for non-contiguous logical ranges; callers free it when it is not the supplied single-record buffer.

## Repair and Risk Notes

The implementation is intentionally simpler than libxfs bmap code because repair mostly needs read-only mapping from already decoded inode forks. The main risks are capacity overflow, preserving sorted insertion order, and caller ownership of temporary arrays from `blkmap_getn`.
