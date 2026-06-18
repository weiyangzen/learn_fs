# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_stats.h

Defines the global/per-mount XFS statistics layout and update macros.

Key elements:
- `__XBTS_*` enumerates fixed per-btree operation counter offsets: lookup, compare, insert/delete record, root changes, shifts, splits, joins, allocations, frees, and moves.
- `struct __xfsstats` is the canonical ordered counter layout. It contains allocator, bmap, directory, transaction, inode, log, AIL, buffer, btree v2, quota, zoned GC, metafile, and 64-bit high precision counters.
- `xfsstats_offset(field)` converts a struct member offset to a 32-bit counter index.
- `struct xfsstats` overlays the named struct with a 32-bit array for offset-based updates.
- `XFS_STATS_CALC_INDEX` computes field indexes for code that stores counter bases, notably btree cursors.

Update macros:
- `XFS_STATS_INC`, `XFS_STATS_DEC`, and `XFS_STATS_ADD` update both global `xfsstats` and per-mount `mp->m_stats`.
- `_OFF` variants update by numeric offset, used by generic btree/stat indexing paths.
- `xfs_init_procfs` and `xfs_cleanup_procfs` are real declarations only when `CONFIG_PROC_FS` is enabled; otherwise inline no-op stubs are provided.

Research notes:
- Layout stability matters because `xfs_stats_format` walks counters by raw offset.
- The 64-bit fields are not handled through the 32-bit array macros; they are explicitly summed in `xfs_stats_format`.
- `XFS_STATS_DEC_OFF` as written only evaluates the indexed counters and does not decrement them, unlike the named decrement macro. Check callers before relying on offset decrement semantics.
