# File Research: sources/os/linux/linux/fs/xfs/xfs_exchrange.c

Implements XFS range-exchange ioctls: `XFS_IOC_EXCHANGE_RANGE`, `XFS_IOC_START_COMMIT`, and `XFS_IOC_COMMIT_RANGE`. The core path validates two regular read/write files on the same mount, locks IO/MMAP state, flushes and unmaps page cache, cancels speculative CoW mappings, reserves quota, exchanges mappings via `xfs_exchmaps`, and updates timestamps/fsnotify.

Key logic:
- `xfs_exchrange_ilock` / `xfs_exchrange_iunlock` lock one or two inodes in a deadlock-safe order and optionally join them to a transaction.
- `xfs_exchrange_estimate` wraps `xfs_exchmaps_estimate` under inode locks.
- `xfs_exchrange_check_freshness` enforces commit-range optimistic concurrency by comparing file2 inode number, generation, ctime, and mtime against a prior snapshot.
- `xfs_exchrange_reserve_quota` computes net and gross data/realtime block deltas and reserves quota for both inodes, retrying after blockgc on `EDQUOT`/`ENOSPC`.
- `xfs_exchrange_mappings` builds an `xfs_exchmaps_req`, rounds realtime allocation units, estimates resources, allocates a write transaction, checks forks, handles dry-run, applies cmtime flags, calls `xfs_exchange_mappings`, commits synchronously when needed, and swaps incore sizes for whole-file-to-EOF exchanges.
- `xfs_exchange_range_checks` performs generic byte-range validation: immutable/swapfile rejection, EOF bounds, to-EOF length derivation, allocation-unit alignment, overflow checks, file size limits, same-file overlap rejection, and partial EOF-block safety.
- `xfs_exchrange_check_rtalign` handles non-power-of-two realtime allocation alignment with division-based checks.
- `xfs_exchrange_prep` enforces matching realtime/non-realtime status, performs generic prep, optional freshness check, quota attachment, range flush/unmap, and CoW cancellation.
- `xfs_exchange_range` is the VFS-facing dispatcher that checks file modes, append state, `remap_verify_area`, timestamp policy, write-start/end nesting, and fsnotify.
- `xfs_ioc_start_commit` samples file2 freshness into an opaque userspace blob containing fsid, inode identity, generation, ctime, and mtime.
- `xfs_ioc_commit_range` validates that blob and reruns exchange with the internal freshness-check flag.

Dependencies include `xfs_exchmaps`, quota, reflink, transaction/log, inode locking, realtime bitmap helpers, `remap_verify_area`, and fsnotify. The file is careful about ordering: freshness checks happen after metadata locks, data is flushed before mapping exchange, and cmtime updates are part of the transaction that exchanges extents.
