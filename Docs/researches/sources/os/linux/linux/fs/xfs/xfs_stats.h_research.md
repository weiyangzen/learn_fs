# File Research: sources/os/linux/linux/fs/xfs/xfs_stats.h

## Purpose

`xfs_stats.h` defines the in-memory XFS statistics layout, btree stat offsets, per-CPU update macros, and procfs initialization stubs. It is the central contract between XFS subsystems that increment counters and the reporting code that formats them.

## Main Interfaces

- `enum __XBTS_*`: fixed offsets for per-btree operation counters such as lookup, compare, insert record, split, join, alloc, free, and moves.
- `struct __xfsstats`: concrete counter layout for all exported XFS statistics.
- `struct xfsstats`: union of structured fields and a 32-bit array used for offset-based counter access.
- `xfsstats_offset(f)` and `XFS_STATS_CALC_INDEX(member)`: convert field names to 32-bit counter indexes.
- `XFS_STATS_INC`, `XFS_STATS_DEC`, `XFS_STATS_ADD`: update named fields in both global and per-mount stats.
- `XFS_STATS_INC_OFF`, `XFS_STATS_DEC_OFF`, `XFS_STATS_ADD_OFF`: update counters by precomputed offset.
- `xfs_stats_format`, `xfs_stats_clearall`, `xfs_init_procfs`, `xfs_cleanup_procfs`: declarations or no-op stubs depending on config.

## Counter Families

- Allocation counters: extents and blocks allocated/freed.
- Btree counters: legacy allocation/bmap counters and version 2 arrays for `abtb`, `abtc`, `bmbt`, `ibt`, `fibt`, `rmap`, `refcnt`, memory btrees, realtime rmap/refcount, and rcbag.
- Mapping, directory, transaction, inode lookup/reclaim, log, AIL push, read/write, attribute, inode cluster, and buffer counters.
- Quota manager counters for dquot reclaim/cache activity.
- Zoned GC counters and metafile inode counters.
- 64-bit precision counters for byte totals and deferred operation relogging.

## Implementation Notes

- The 32-bit array in `struct xfsstats` ends at `xs_qm_dquot`, so offset-based access is intended for the fixed-width 32-bit counter region. The 64-bit counters are handled separately by format/clear code.
- Update macros use `current_cpu()` and directly access per-CPU storage for both `xfsstats.xs_stats` and `mp->m_stats.xs_stats`.
- The btree stat comments explicitly require appending new btree stat types to preserve output ordering and cursor index assumptions.
- `XFS_STATS_DEC_OFF` appears to evaluate the selected counter slots without decrementing them. Research consumers should verify whether the macro is unused, intentionally inert, or a bug candidate in this kernel snapshot.

## Dependencies and Callers

- Included by XFS code that needs to update counters, and by `xfs_stats.c` for formatting.
- The procfs declarations are active only with `CONFIG_PROC_FS`; otherwise the init and cleanup functions compile to no-ops.

## Research Notes

- This header is ABI-sensitive because user-visible stat output depends directly on structure field order.
- Any extension to counters must coordinate `struct __xfsstats`, `xfs_stats_format` grouping, and any users that compute `XFS_STATS_CALC_INDEX`.
