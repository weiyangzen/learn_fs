# File Research: sources/os/linux/linux/fs/f2fs/shrinker.c

Read completely: 246 lines.

## Purpose
Implements F2FS shrinker integration and explicit cache reclamation across mounted F2FS instances.

## Main Responsibilities
- Maintains a global list of F2FS superblocks participating in shrinker scans.
- Counts reclaimable read extent cache, block-age extent cache, clean NAT entries, and excess free NID entries.
- Reclaims those caches when the kernel shrinker asks F2FS to scan.
- Tracks and reclaims donated inode page-cache ranges for explicit cache donation/reclaim flows.
- Adds/removes filesystems from the shrinker list at mount/unmount lifecycle boundaries.

## Key Functions
- `__count_nat_entries()` returns reclaimable clean NAT cache entries.
- `__count_free_nids()` returns free-NID cache entries above `MAX_FREE_NIDS`.
- `__count_extent_cache()` sums zombie extent trees and extent nodes for a given extent type.
- `f2fs_shrink_count()` walks all mounted F2FS instances and returns total reclaimable objects or `SHRINK_EMPTY`.
- `f2fs_shrink_scan()` assigns a nonzero run id, walks the global list, shrinks age extents, read extents, NATs, and free NIDs, then rotates scanned filesystems to the tail for fairness.
- `f2fs_donate_files()` totals per-filesystem donated-file counts.
- `do_reclaim_caches()` iterates donated inodes, invalidates the configured page-cache range, and marks `FI_DONATE_FINISHED`.
- `f2fs_reclaim_caches()` applies donated-cache reclamation across mounted filesystems until the requested kilobyte budget is exhausted.
- `f2fs_join_shrinker()` and `f2fs_leave_shrinker()` manage global shrinker list membership; leave also drains extent caches for that filesystem.

## Concurrency and State
- `f2fs_list_lock` protects the global `f2fs_list` and list traversal.
- Each filesystem’s `umount_mutex` is acquired with `mutex_trylock()` to avoid racing `f2fs_put_super()`; locked filesystems are skipped rather than blocking.
- `shrinker_run_no` prevents revisiting the same filesystem during one shrink scan after list rotation.
- Donated inode lists use `sbi->inode_lock[DONATE_INODE]`; inodes are pinned with `igrab()`, locked with `inode_lock()`, then released with `iput()`.

## Important Edge Cases
- Shrinker counting/scanning skips filesystems currently unmounting.
- `shrinker_run_no` intentionally skips zero by incrementing until nonzero.
- Reclaim budget is split initially between age/read extent shrinking with `nr >> 2`, then remaining budget is used for NAT and free-NID caches.
- Donated-cache reclaim converts kilobytes to pages and returns the unreclaimed kilobyte budget.
- If an inode cannot be grabbed, reclaim continues with the next donated inode.
