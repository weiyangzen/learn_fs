# File Research: sources/os/linux/linux/fs/f2fs/gc.c

Read completely: 2426 lines.

## Summary
Implements F2FS garbage collection, including the background GC kernel thread, victim selection policies, age-threshold GC, SSR victim lookup support, pinned-section handling, node/data block migration, GC range execution, GC manager setup, and filesystem shrink/resize support.

## Main Responsibilities
- Starts, stops, and runs the background GC thread.
- Selects victim segments/sections for background GC, foreground GC, SSR, and age-threshold GC.
- Maintains temporary victim rb-trees for age-based selection.
- Migrates valid node and data blocks out of victim segments.
- Handles pinned files and pinned sections during GC.
- Reclaims sections until free-space requirements are met, checkpointing when needed.
- Provides GC over explicit ranges and supports online filesystem shrink.

## Key APIs
- Thread lifecycle: `f2fs_start_gc_thread()`, `f2fs_stop_gc_thread()`, `gc_thread_func()`.
- Victim selection: `f2fs_get_victim()`, `select_policy()`, `get_gc_cost()`, `lookup_victim_by_age()`.
- Migration: `gc_node_segment()`, `gc_data_segment()`, `move_data_block()`, `move_data_page()`, `ra_data_block()`.
- Main GC flow: `f2fs_gc()`, `do_garbage_collect()`, `f2fs_gc_range()`.
- Resize/shrink: `f2fs_resize_fs()`, `free_segment_range()`, `update_sb_metadata()`, `update_fs_metadata()`.
- Cache lifecycle: `f2fs_create_garbage_collection_cache()`, `f2fs_destroy_garbage_collection_cache()`.
- Setup: `f2fs_build_gc_manager()`.

## Important Behavior
The GC thread adapts sleep time based on urgent modes, free space, dirty/invalid block ratios, zoned-device thresholds, foreground-GC merge requests, and I/O idleness. It acquires `gc_lock`, chooses foreground or background mode, calls `f2fs_gc()`, wakes merged foreground waiters, and periodically balances metadata.

Victim selection supports greedy, cost-benefit, age-threshold GC, SSR, and AT_SSR. It scans dirty bitmaps, honors max-search limits, skips current sections and busy sections, handles checkpoint-disabled constraints, avoids background-selected victims unless foreground GC can consume them, and tracks `last_victim` cursors.

Age-threshold GC stores candidate sections in a temporary rb-tree ordered by mtime, then combines age and utilization cost. AT_SSR searches around a target age and prioritizes low checkpoint-valid block counts.

Node GC validates summary NAT information, readaheads NAT and node pages in phases, verifies the current NAT block address still points at the victim block, then rewrites node folios cold.

Data GC is phased: NAT readahead, node readahead, liveness validation, inode/data readahead, then migration. It validates that the node still references the victim block, obtains the owning inode, avoids inline-data contradictions, handles meta-inode GC through `META_MAPPING`, and migrates either by page writeback or direct block copying.

`f2fs_gc()` escalates to foreground GC when free sections are insufficient, checkpoints prefree segments when that can reclaim space, loops until requirements are met, and stops after too many skipped inode GC locks by checkpointing. It unpins pinned sections after foreground GC.

Resize shrink first dry-runs evacuation of the tail sections, freezes the filesystem, updates in-memory and on-disk geometry, commits the superblock, updates checkpoint-visible metadata, writes a resize checkpoint, and marks fsck-needed on recovery failures.

## State and Synchronization
Uses `gc_lock`, dirty segment list mutex, SIT sentry locks, pinned section bitmaps, victim section bitmaps, `next_victim_seg`, `cur_victim_sec`, radix-tree GC inode lists, folio locks, `i_gc_rwsem`, direct-I/O waits, blk plugs, checkpoint locks, freeze/thaw, and superblock locks. Victim entries are allocated from `f2fs_victim_entry`.

## Risks
GC correctness depends on summary, NAT, SIT valid maps, and node data addresses agreeing at migration time. Race handling is defensive, but stale or corrupted metadata can skip blocks, stop checkpoints, or set `SBI_NEED_FSCK`. Pinned files can repeatedly block foreground GC and are tracked as a risk signal. Resize has high blast radius because it temporarily changes `MAIN_SECS`, moves current segments, performs GC, mutates superblock geometry, and relies on checkpoint recovery.
