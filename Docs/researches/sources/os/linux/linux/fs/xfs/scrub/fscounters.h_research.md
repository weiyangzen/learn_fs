# File Research: sources/os/linux/linux/fs/xfs/scrub/fscounters.h

Defines `struct xchk_fscounters`, the shared scrub/repair state for filesystem summary counters.

Fields:
- `sc`: owning scrub context.
- `icount`, `ifree`, `fdblocks`: recomputed global inode, free inode, and free data-block counts.
- `frextents`, `frextents_delayed`: recomputed free realtime extent count and delayed realtime extent reservations.
- `icount_min`, `icount_max`: legal inode-count bounds.
- `frozen`: whether setup froze the filesystem and cleanup must thaw it.

This state is filled by scrub and consumed by `fscounters_repair.c`.
