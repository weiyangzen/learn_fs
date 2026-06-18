# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ufs_dirhash.c

## Purpose

Implements optional hash-accelerated lookup and free-space tracking for large UFS directories when `UFS_DIRHASH` is enabled.

## Main Data And Tunables

- Allocator: `M_DIRHASH`.
- Sysctls:
  - `vfs.ufs.dirhash_minsize`: minimum directory size for hashed lookup.
  - `vfs.ufs.dirhash_maxmem`: global memory cap.
  - `vfs.ufs.dirhash_mem`: current memory use.
  - `vfs.ufs.dirhash_docheck`: optional consistency checks.
- Global LRU-like list: `ufsdirhash_list`.
- Object cache: `ufsdirhash_oc`, used for hash array blocks.

## Main Functions

- `ufsdirhash_build()`: builds a hash table and per-directory-block free-space summaries from existing directory contents.
- `ufsdirhash_free()`: releases hash arrays, free-space arrays, and the dirhash object.
- `ufsdirhash_lookup()`: looks up a name through linear probing, validates candidate directory entries, supports sequential-access optimization, and can return the previous entry offset for delete.
- `ufsdirhash_findfree()`: finds a directory block with enough free space for insertion.
- `ufsdirhash_enduseful()`: identifies trailing fully free directory blocks that could be truncated.
- `ufsdirhash_add()`, `ufsdirhash_remove()`, `ufsdirhash_move()`: maintain hash state as directory entries are inserted, removed, or compacted.
- `ufsdirhash_newblk()` and `ufsdirhash_dirtrunc()`: update state when a directory grows or shrinks.
- `ufsdirhash_checkblock()`: optional sanity checker that compares hash/free-space state to actual directory block contents.
- Static helpers implement hashing, free-space bucket updates, slot lookup/deletion, previous-entry discovery, recycling, and initialization.

## Important Behavior

Hash entries store directory offsets, not inode numbers. Collisions use linear probing with `DIRHASH_EMPTY` and `DIRHASH_DEL` sentinels. The filename hash mixes FNV-1 with the `dirhash` object address to reduce clustering for similar names.

Memory pressure is handled by recycling the lowest-scored dirhash entries from the head of `ufsdirhash_list`. Recycling detaches only the heavy hash/free arrays and leaves an inode-associated `dirhash` shell that later lookup code can detect and free/rebuild.

## Dependencies And Integration Points

Used by `ufs_lookup.c` during lookup, insertion, deletion, compaction, directory growth, and truncation. Depends on `dirhash.h`, `dir.h`, `inode.h`, `ufsmount.h`, `ffs_extern.h`, buffer cache reads through `ffs_blkatoff()`, and FNV hashing.

## Notes For Future Work

- All logic is inside `#ifdef UFS_DIRHASH`; callers must tolerate absence of these helpers.
- The code frequently falls back to linear search by returning `EJUSTRETURN` or `-1` when corruption, stale state, or allocation limits are encountered.
- Directory corruption checks are defensive; several paths free or abandon a hash instead of trusting inconsistent state.
