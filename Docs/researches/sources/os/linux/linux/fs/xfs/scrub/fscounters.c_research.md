# File Research: sources/os/linux/linux/fs/xfs/scrub/fscounters.c

Scrubs global filesystem summary counters: inode count, free inode count, free data blocks, and free realtime extents. It recomputes expected values from per-AG/per-RT metadata and compares those values to in-core percpu counters, with tolerance for live filesystem activity unless repair or try-harder mode freezes the filesystem.

Main flow:
- `xchk_fscount_warmup` walks AGs and reads AGI/AGF headers as needed so per-AG in-core counters are initialized before fast aggregation.
- `xchk_fsfreeze`, `xchk_fsthaw`, `xchk_fscounters_freeze`, and `xchk_fscounters_cleanup` manage kernel freeze/thaw for stable counter checking or repair.
- `xchk_setup_fscounters` allocates `struct xchk_fscounters`, computes legal inode-count range, warms per-AG state, optionally freezes the filesystem, and starts an empty transaction.
- `xchk_fscount_btreeblks` manually counts free-space btree blocks for filesystems without lazy superblock counters.
- `xchk_fscount_aggregate_agcounts` sums per-AG inode/free/freeblock counters, btree blocks, freelist blocks, and subtracts per-AG reservations, global reservation, and delayed allocation reservations.
- `xchk_fscount_count_frextents` counts free realtime extents from rt bitmap data when applicable; the non-RT build returns zero counts.
- `xchk_fscount_within_range` compares expected values to before/after percpu counter snapshots. Exact matches are required for repair; non-repair scans tolerate expected values between the two snapshots.
- `xchk_fscounters` snapshots counters, rejects impossible values, recomputes expected counts, compares each counter, marks corruption if frozen and mismatched, or returns `-EDEADLOCK` to request a retry with stronger protection.

Important behavior:
- Lockless aggregation can race with live allocation, so non-frozen mismatches are treated as retryable when plausible.
- Incomplete aggregation must set `INCOMPLETE` to prevent repair from using insufficient data.
- Zoned realtime filesystems skip frextents verification because their counters include reservations differently.
