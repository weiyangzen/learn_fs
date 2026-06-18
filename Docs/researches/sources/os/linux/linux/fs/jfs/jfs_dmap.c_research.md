# File Research: sources/os/linux/linux/fs/jfs/jfs_dmap.c

## Purpose
Implements the JFS aggregate block allocation map: mount/unmount synchronization, working and persistent bitmap updates, allocation/free policies, allocation-group selection, discard scanning, filesystem extension, and dmap/dmapctl buddy-summary tree maintenance.

## Architecture
- The allocator uses dmap pages for 8192-block bitmap chunks and dmapctl pages for multi-level summary trees.
- Working allocation state uses `dmap.wmap`; committed persistent allocation state uses `dmap.pmap`.
- Summary trees store log2 maximum free-buddy sizes, with `NOFREE` meaning no free blocks in a subtree.
- Allocation groups (`AG`s) track per-group free counts and active-writer counts to reduce fragmentation.
- Bottom-up operations hold `IREAD_LOCK(ipbmap, RDWRLOCK_DMAP)` and serialize through busy metapages plus `BMAP_LOCK` for global counters.
- Top-down searches hold `IWRITE_LOCK(ipbmap, RDWRLOCK_DMAP)` to exclude other map traversals.

## Mount, Unmount, and Sync
- `dbMount()` allocates `struct bmap`, reads the on-disk global map descriptor, converts little-endian fields, validates descriptor ranges, initializes active counters and the bmap mutex, and attaches it to `JFS_SBI(sb)->bmap`.
- `dbUnmount()` syncs the bmap unless read-only or mount-error, truncates bmap inode pages, frees the descriptor, and clears the superblock pointer.
- `dbSync()` writes in-memory global bmap fields back to the on-disk descriptor, writes dirty bmap pages, and calls `diWriteSpecial()`.

## Integrity Checks
- `check_dmapctl()` validates dmapctl metadata before tree descent/update: leaf count bounds, power-of-two leaf count, expected leaf index, height, `budmin`, leaf range bounds, and leaf value range.
- This check is used in `dbAllocAG()`, `dbFindCtl()`, `dbAdjCtl()`, and `dbExtendFS()` before relying on dmapctl tree fields.
- Additional checks reject corrupt dmap pages with unexpected `leafidx`, negative dmap `budmin`, inconsistent control pages, and invalid buddy tree states.

## Allocation and Freeing
- `dbFree()` validates range bounds, optionally issues online discard when mounted with `JFS_DISCARD`, then frees blocks dmap-by-dmap through `dbFreeDmap()`.
- `dbUpdatePMap()` updates the persistent bitmap for a transaction, dmap-by-dmap, and attaches metapages to log sync lists with appropriate `lsn`/`clsn`.
- `dbNextAG()` chooses a preferred inactive AG with at least average free space, falling back to the best inactive AG below average.
- `dbAlloc()` is the main allocation policy:
  - Large requests above AG size go directly to `dbAllocAny()`.
  - Hintless requests use `dbNextAG()`.
  - Hinted small requests try immediate next blocks, nearby leaves, the same dmap, the same AG, preferred AG, then anywhere.
  - Active-writer AG counters can push allocation away from busy AGs.
- `dbReAlloc()` first tries in-place extension through `dbExtend()`, then allocates a larger new range if extension fails with `-ENOSPC`.
- `dbExtend()` attempts to allocate blocks immediately after an existing range, with page-boundary and AG-boundary constraints.
- `dbAllocAG()` searches a specified AG through dmapctl subtrees or direct dmap allocation for minimum-size/free AG cases.
- `dbAllocAny()` searches from the top dmapctl level, then allocates through `dbAllocCtl()`.
- `dbAllocCtl()` allocates from a dmap or across multiple all-free dmaps; on multi-dmap failure it attempts to back out partial allocations.
- `dbAllocDmapLev()` searches one dmap tree for a suitable leaf and allocates from it.
- `dbAllocDmap()` and `dbFreeDmap()` update one dmap and propagate changed root values upward through `dbAdjCtl()`.
- `dbAllocBottomUp()` and `dbAllocDmapBU()` allocate a specified range during resize/setup-style paths and reconstruct the dmap tree afterward.

## Bitmap and Buddy Tree Maintenance
- `dbAllocBits()` sets working-map bits, splits buddy leaves through `dbSplit()`, updates dmap free count, AG free count, global free count, and `db_maxag`.
- `dbFreeBits()` clears working-map bits, joins buddies through `dbJoin()`, updates counts, and may move `db_maxag`/`db_agpref` left when rightmost AGs become fully free.
- `dbAdjCtl()` updates the dmapctl leaf corresponding to a lower-level root change, recursively bubbles root changes upward, and updates `db_maxfreebud` at the top.
- `dbSplit()` splits a larger buddy system down to the requested size before applying a new leaf value.
- `dbBackSplit()` handles rare allocations or rollbacks that start in the middle of a larger buddy system.
- `dbJoin()` coalesces equal-sized buddy leaves into larger free systems and rejects inconsistent buddy values with `-EIO`.
- `dbAdjTree()` updates a leaf and bubbles max values up a 4-way summary tree with bounds checking.
- `dbFindLeaf()` finds the leftmost leaf with sufficient free space in dmap or dmapctl trees.
- `dbFindBits()` scans a 32-bit bitmap word for aligned free bits.
- `dbMaxBud()` uses `budtab` plus word/halfword checks to compute the largest free buddy in one map word.
- `cnttz()`, `cntlz()`, and `blkstol2()` provide bit-count/log2 helpers used by macros and allocation sizing.

## Discard and Trim
- `dbDiscardAG()` trims free space in one AG by temporarily allocating large free ranges while holding the bmap write lock, storing up to 32K ranges, releasing the lock, issuing discard for each saved range unless online discard will do it through `dbFree()`, freeing the ranges, and returning blocks trimmed.
- This is called by `jfs_ioc_trim()` in `jfs_discard.c`.

## Filesystem Extension
- `dbExtendFS()` expands the bmap for new blocks, recomputes map size, max level, AG size/count, coalesces old AG free counts if AG size changes, reads or initializes L2/L1/L0/dmap pages, initializes new dmaps with `dbInitDmap()`, updates parent control leaves, and updates free counters.
- `dbFinalizeBmap()` recomputes preferred AG, AG tree level/height/width/start after extension.
- `dbInitDmap()` initializes a dmap's working/persistent maps for existing and non-existing blocks and builds its summary tree.
- `dbInitDmapTree()` initializes dmap tree fixed fields and leaf values from `wmap`.
- `dbInitTree()` coalesces leaf-level buddies and bubbles summary values upward.
- `dbInitDmapCtl()` initializes a dmapctl page and marks leaves outside the covered range as `NOFREE`.
- `dbGetL2AGSize()` derives allocation group size from aggregate size.
- `dbMapFileSizeToMapSize()` computes the aggregate block coverage possible from the bmap file size.

## Dependencies
- Uses `jfs_dmap.h` for constants, structures, and conversion macros.
- Uses metapage I/O, transaction/log sync structures, inode/superblock state, JFS locks, discard support, and debug/error helpers.
- Called indirectly from extent allocation/truncation code and directly from discard and mount/resize paths.

## Notable Risks and Invariants
- Bitmap, dmap tree, dmapctl tree, global free counts, and AG free counts must remain synchronized; many paths back out on propagation failure.
- Multi-dmap allocation expects complete dmaps to be all free; otherwise it treats the map as inconsistent.
- Persistent map updates are transaction/log-sensitive and distinct from working-map updates.
- Discard temporarily allocates free blocks as a scanning mechanism, so errors during later free would affect allocation-map consistency.
