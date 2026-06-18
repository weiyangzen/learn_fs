# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/fscounters.c

This file scrubs XFS filesystem summary counters: inode count, free inode count, free data blocks, and free realtime extents. It computes expected values from incore AG and realtime metadata, compares them with percpu/global counters, and decides whether discrepancies are corruption or live-race noise.

Key state:
- Uses `struct xchk_fscounters` from `fscounters.h`.
- `XCHK_FSCOUNT_MIN_VARIANCE` provides minimum tolerance for unfrozen live scans.

Setup and freeze behavior:
- `xchk_setup_fscounters` allocates state, records valid inode count bounds, warms per-AG AGI/AGF state, optionally freezes the filesystem for repair or try-harder scans, and allocates an empty transaction.
- `xchk_fscount_warmup` reads AGI/AGF headers for any uninitialized per-AG state.
- `xchk_fscounters_freeze` drops write protection if held, repeatedly tries a kernel freeze, and marks the state frozen.
- `xchk_fscounters_cleanup` thaws on cleanup and logs emergency if thaw fails.

Counting behavior:
- `xchk_fscount_aggregate_agcounts` sums per-AG inode/free inode/free block values, includes freelist and btree blocks, subtracts per-AG and global reservations, subtracts delayed allocation blocks, and rejects nonsensical totals.
- For non-lazy sbcount filesystems, `xchk_fscount_btreeblks` counts bno/cnt btree blocks directly.
- Realtime support counts free realtime extents by querying each rtgroup bitmap and accounts for delayed realtime allocations; zoned filesystems skip frextents checks.

Comparison behavior:
- `xchk_fscount_within_range` accepts exact matches, or for non-repair live scans accepts expected values between before/after percpu sums.
- `xchk_fscounters` snapshots counters, rejects negative or impossible values, computes expected counters, counts realtime extents, compares all counters, and returns `-EDEADLOCK` when an unfrozen live scan needs userspace to retry with stronger stabilization.

Important invariants:
- Any counting failure marks the scrub incomplete so repair will not use partial data.
- Repair requires exact counter matches and a frozen filesystem.
- Negative free counters during an unfrozen scan can be transient due to racing reservations; frozen negatives are corruption.

Risks and edge cases:
- Busy live filesystems can produce `-EDEADLOCK` rather than false corruption.
- Pre-lazysbcount filesystems require deeper btree block counting.
- Zoned filesystems intentionally avoid on-disk frextents repair semantics.
