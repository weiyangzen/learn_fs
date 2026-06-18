# File Research: sources/os/linux/linux-stable/fs/f2fs/debug.c

`debug.c` implements F2FS runtime statistics collection and the debugfs status report. It maintains a global `f2fs_stat_list` protected by `f2fs_stat_lock`; each mounted filesystem that builds stats contributes one `f2fs_stat_info`.

`f2fs_update_sit_info()` computes segment-distribution diagnostics, including the bimodal distribution factor and average valid blocks across dirty sections. With debugfs enabled, `update_multidevice_stats()` classifies each device’s segments, and sections for large-section filesystems, into in-use, dirty, full, free, and prefree buckets.

`update_general_status()` snapshots a broad set of live counters into `f2fs_stat_info`: superblock layout, extent-cache hits and object counts, dirty page/inode counts, direct I/O and writeback counts, flush/discard queues, checkpoint merge timing, valid/free/prefree/dirty segment counts, inline/compressed/swapfile inode counters, NAT/SIT/free-NID state, GC skip counts, current segment positions, metadata block counts, checkpoint call counts, SSR/LFS block counts, and inplace-update count.

`update_mem_info()` estimates F2FS memory footprint. It separates base/static filesystem structures, cached metadata structures such as NAT/SIT/dirty/free maps and extent cache nodes, and mapped page-cache memory for node/meta/compress inodes.

`stat_show()` is the debugfs `.show` callback. It locks the global stat list, updates each mounted filesystem’s status, and emits a human-readable report covering partition state, checkpoint state, SBI flags, layout, mount time, IPU policy, utilization, inode/data breakdown, curseg positions, multidevice stats, checkpoint and GC activity, extent-cache ratios, async I/O pressure, dirty data distribution, SSR/LFS/IPU counts, segment BDF, and memory usage.

`f2fs_build_stats()` allocates and initializes per-mount stat state, initializes stat counters on `sbi`, attaches the entry to the global list, and stores it in `sbi->stat_info`. `f2fs_destroy_stats()` removes and frees it. `f2fs_create_root_stats()` creates `/sys/kernel/debug/f2fs/status`, and `f2fs_destroy_root_stats()` removes the debugfs tree.

This file is observability-focused: it does not implement filesystem mutation paths, but it reads many live F2FS subsystem counters. Its main safety concerns are locking around the global list, checkpoint timing stat lock, extent/multidevice data consistency during reporting, and keeping debugfs-only code behind `CONFIG_DEBUG_FS`.
