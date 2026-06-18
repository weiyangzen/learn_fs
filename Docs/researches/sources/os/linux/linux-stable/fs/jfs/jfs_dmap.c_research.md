# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_dmap.c

Large JFS aggregate block allocation map implementation. It maintains working/persistent bitmaps, dmap summary trees, dmap control pages, allocation-group free counts, preferred AG selection, filesystem resize map extension, and discard enumeration.

Major areas:
- Mount/sync: `dbMount()` reads and validates the on-disk bmap descriptor, initializes locks/active AG counters; `dbSync()` writes it back; `dbUnmount()` syncs and frees state.
- Free/persistent update: `dbFree()` frees working-map blocks dmap by dmap and optionally issues online discard; `dbUpdatePMap()` updates persistent map bits and logsync metadata.
- Allocation policy: `dbAlloc()` tries next-to-hint, near-hint, same dmap, same AG, preferred AG, then anywhere; `dbNextAG()` avoids active writers and chooses an AG with average free space.
- Reallocation: `dbReAlloc()` first attempts in-place extension via `dbExtend()`, then falls back to allocating a larger new extent.
- Top-down search: `dbAllocAG()`, `dbAllocAny()`, `dbFindCtl()`, and `dbAllocCtl()` traverse dmapctl trees to find sufficient contiguous free space.
- Dmap mutation: `dbAllocDmap()`, `dbFreeDmap()`, `dbAllocBits()`, and `dbFreeBits()` update working bitmaps, leaf summaries, global/per-AG free counters, and parent control pages.
- Buddy tree maintenance: `dbSplit()`, `dbBackSplit()`, `dbJoin()`, `dbAdjTree()`, `dbFindLeaf()`, `dbFindBits()`, and `dbMaxBud()` maintain binary-buddy summaries over bitmap words/control pages.
- Discard: `dbDiscardAG()` temporarily allocates free extents within an AG, issues discard, then frees them again.
- Resize/init: `dbAllocBottomUp()`, `dbExtendFS()`, `dbFinalizeBmap()`, `dbInitDmap()`, `dbInitDmapTree()`, `dbInitTree()`, `dbInitDmapCtl()`, `dbGetL2AGSize()`, and `dbMapFileSizeToMapSize()` build or extend map coverage.

Serialization:
- Bottom-up dmap operations use `IREAD_LOCK`; top-down allocation/search uses `IWRITE_LOCK`.
- `BMAP_LOCK` protects aggregate counters such as `db_nfree`, `db_agfree`, `db_maxag`, and `db_agpref`.
- Busy metapages serialize persistent bitmap/control-page contents.

Integrity checks:
- `check_dmapctl()` validates dmapctl field ranges, tree shape, leaf index, height, budmin, leaf bounds, and leaf values before use.
- Allocation/free paths treat summary inconsistency as `-EIO` and call `jfs_error()` in several impossible-state branches.
- Multi-dmap allocation has a backout loop to avoid leaked blocks; failures during backout mark block leakage.

Risk notes:
- The allocator depends on precise buddy-tree invariants; incorrect split/join/backsplit handling can corrupt free-space summaries.
- Some bounds checks use assertions in paths where corrupt disk state may still be possible; newer explicit checks exist for dmapctl but not every dmap tree access.
- `dbDiscardAG()` intentionally mutates allocation state to find trim ranges, then restores it, so interruption/error paths are sensitive.
