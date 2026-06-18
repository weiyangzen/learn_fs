# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_extent.c

This file implements regular-file extent allocation support for JFS. It chooses block ranges, inserts or extends xtree records, preserves not-recorded extent state, and provides allocation hints.

Key responsibilities:
- Allocates an extent for a file page range in `extAlloc()`, with read-only checks, anonymous transaction setup, commit mutex serialization, quota charging, block allocation, and xtree insertion/extension.
- Caps requested extents at `MAXXLEN` and converts page numbers to filesystem block offsets using the mounted block geometry.
- Uses a caller-provided `xad_t` as an allocation hint and extends the previous extent when the new allocation is contiguous and has matching recorded/not-recorded state.
- Falls back to smaller allocation sizes through `extBalloc()` when the requested contiguous extent is unavailable, rounding down toward power-of-two sizes while preserving at least one page of blocks.
- Produces previous-page allocation hints in `extHint()` by looking up the page before the requested offset and returning its extent descriptor when it exactly covers one page.
- Converts not-recorded extents to recorded state through `extRecord()`, delegating to `xtUpdate()`.
- Tracks the active allocation group for growing regular files so the block allocator can avoid fragmentation-sensitive placement conflicts.

Important interactions:
- Calls the JFS block allocator (`dbAlloc()`, `dbFree()`) and xtree operations (`xtInsert()`, `xtExtend()`, `xtLookup()`, `xtUpdate()`).
- Uses quota helpers to charge and roll back block allocation.
- Uses `JFS_IP(ip)->commit_mutex` to serialize extent-tree updates against inode commit.
- May force inode commit when `COMMIT_Synclist` is cleared after anonymous metadata updates.

Notable invariants and risks:
- Extent offsets are filesystem-block offsets derived from page numbers, not byte offsets.
- The allocation hint can only be extended when the old extent ends exactly at the requested offset and the `XAD_NOTRECORDED` state matches.
- Failed xtree insertion/extension must free both allocated blocks and quota charges.
- `extHint()` treats a previous-page extent with a length other than one page as xtree corruption.
- `extBalloc()` must never return an allocation smaller than the filesystem blocks per page.

Research notes:
- This file is a narrow bridge between file write/page allocation and the lower JFS block map plus xtree metadata. It does not perform buffered I/O itself; it updates file extent metadata for callers elsewhere in JFS.
