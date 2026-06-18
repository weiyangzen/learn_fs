# File Research: sources/local-fs/xfsprogs/repair/xfs_repair.c

Main program driver for `xfs_repair`.

Major responsibilities:
- Parses command-line options and conversion/override suboptions.
- Initializes libxfs, mount state, caches, progress, block maps, inode maps, rmap state, and rtgroup inode tracking.
- Orchestrates phases 1 through 7.
- Protects modified CRC filesystems with `NEEDSREPAIR`.
- Handles final quota, secondary-super, realtime-super, log, flush, unmount, and exit-code behavior.

Important functions:
- `process_args` handles `-n`, `-L`, `-m`, `-r`, `-l`, `-o`, `-c`, `-P`, `-t`, `-e`, and debug/failure options.
- `err_string`, `do_error`, `do_abort`, `do_warn`, and `do_log` centralize diagnostics and fatal exits.
- `calc_mkfs` validates fixed-location inode expectations for root, metadata directory, realtime bitmap, and realtime summary.
- `guess_correct_sunit` tries to recover plausible stripe unit from secondary superblocks or root inode placement.
- `format_log_max_lsn` reformats the log if metadata LSNs are ahead of the current log cycle.
- `retain_primary_sb`, `force_needsrepair`, `repair_capture_writeback`, and `clear_needsrepair` manage crash protection during metadata writes.
- `bump_max_fds` raises fd limits for memfd/xfile-heavy repair workloads.

Main flow:
1. Parse arguments, initialize libxfs, and run phase 1 to obtain a valid superblock.
2. Mount libxfs repair context and initialize global geometry/state.
3. Tune parallelism and buffer cache size.
4. Initialize bmaps, inode trees, rmap structures, and rtgroup inode bitmaps.
5. Parse feature/version state.
6. Run phase 2, initialize prefetch, phase 3, rcbag cursor cache, phase 4, phase 5 unless no-modify, phase 6/7 unless inode btrees are too corrupted.
7. Emit quota warnings, stop progress, handle no-modify exit.
8. Update quota flags, secondary superblocks, realtime superblock, flush cache, reformat log if necessary, clear `NEEDSREPAIR`, unmount, and return status.

Important behavior:
- Automatic AG stride/threading increases parallelism on multidisk/high-AG filesystems.
- No-modify mode stops before phase 5 and exits nonzero if dirtiness was detected.
- `-e` returns code 4 if errors were corrected.
- `NEEDSREPAIR` is set before first non-super metadata write and cleared only after successful flush.
