# File Research: sources/os/linux/linux-stable/fs/f2fs/gc.h

`gc.h` defines F2FS garbage-collection tuning constants, GC thread state, victim-entry data structures, and inline free-space/pressure helpers used by `gc.c` and allocation policy.

The constants define default background GC sleep times, urgent sleep time, zoned-device sleep times, age-threshold GC parameters, invalid/free block pressure limits, zoned GC boost thresholds, migration window defaults, pinned-file GC failure limits, victim search limit, and the extra checkpoint sections required during GC pressure.

`struct f2fs_gc_kthread` stores the background GC task, wait queues, sleep-time knobs, urgent wake flag, foreground-GC merge wait queue, zoned GC thresholds, one-time GC valid-block threshold, and boost controls. `struct gc_inode_list` is a temporary radix-tree/list cache of inodes referenced during data GC. `struct victim_entry` is the rb-tree/list node used by age-threshold victim selection.

The free-space helpers account for zoned-device zone capacity. `free_segs_blk_count_zoned()` sums usable blocks in currently free segments instead of assuming all segments have full segment capacity. `free_user_blocks()` subtracts overprovisioned blocks, and the limit helpers compute invalid/free thresholds as percentages of user or reclaimable blocks.

Sleep helpers increase or decrease background GC wait time within configured bounds, with special handling for the no-GC sleep interval. `has_enough_free_blocks()`, `has_enough_invalid_blocks()`, and `need_to_boost_gc()` provide the pressure signals that decide whether background GC should run more aggressively, with zoned devices using free-section percentage rather than invalid-block ratio.

This header is small but policy-critical: changing the constants affects GC latency, write amplification, zoned-device behavior, and when pinned files are eventually unpinned or rejected.
