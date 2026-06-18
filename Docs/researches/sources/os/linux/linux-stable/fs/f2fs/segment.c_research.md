# File Research: sources/os/linux/linux-stable/fs/f2fs/segment.c

Read completely: 5928 lines.

## Purpose
Implements the F2FS segment manager: current segment allocation, SIT validity tracking, dirty/pre-free segment accounting, discard/TRIM scheduling, summary block persistence, flush merging, atomic-write block replacement, block write placement, zoned-device write-pointer handling, and segment-manager lifecycle.

## Main Responsibilities
- Chooses when to use SSR versus LFS allocation and allocates new current segments/sections.
- Maintains SIT entries, valid-block bitmaps, checkpoint-valid bitmaps, discard maps, section counters, and segment mtimes.
- Tracks dirty, pre-free, victim, and pinned sections for GC and checkpoint.
- Queues, merges, issues, waits for, drops, and times out discard commands, including zone reset commands on zoned devices.
- Writes and restores compact/normal current-segment summary blocks and NAT/SIT journals.
- Coordinates metadata/data/node write placement and block replacement for recovery, GC, and atomic writes.
- Builds and destroys all segment-manager in-memory state and slab caches.

## Key Flows
- Atomic writes: `f2fs_commit_atomic_write()` flushes file data, locks GC/write operation state, walks the COW inode, replaces original file blocks via `__replace_atomic_write_block()`, and records a revoke list so failed commits can restore old addresses.
- Filesystem balancing: `f2fs_balance_fs()` and `f2fs_balance_fs_bg()` trigger foreground/background GC, checkpointing, NAT/free-NID cleanup, and extent-cache shrinkage when free sections, dirty metadata, cached NATs, prefree segments, or roll-forward space cross thresholds.
- Flush handling: `f2fs_issue_flush()` either submits directly or merges concurrent flushes through `issue_flush_thread()` and `flush_cmd_control`, with per-device flushing for multi-device filesystems.
- Dirty segment tracking: `locate_dirty_segment()`, `f2fs_dirty_to_prefree()`, and helpers move segments among `DIRTY`, type-specific dirty maps, and `PRE` based on current and checkpoint-valid blocks.
- Discard management: discard ranges are represented as `discard_cmd` nodes in an rb-tree plus size-bucket pending lists. `__update_discard_tree_range()` merges adjacent ranges; `__submit_discard_cmd()` splits requests by device limits; wait paths use command completions and refcounts.
- Checkpoint/TRIM: `f2fs_flush_sit_entries()` writes dirty SIT entries either into the SIT journal or next SIT blocks, gathers discard candidates, and converts pre-free segments to free segments after checkpoint.
- Allocation: `get_new_segment()`, `new_curseg()`, `change_curseg()`, `get_ssr_segment()`, and `need_new_seg()` choose free or reusable segments while respecting active log type, section/zone placement, checkpoint-disabled mode, pinned sections, and ATGC.
- Write placement: `f2fs_allocate_data_block()` updates summaries, SIT maps, mtimes, dirty maps, current-segment offsets, device dirty state, and writeback queues for out-of-place writes. `f2fs_inplace_write_data()` handles IPU writes after validating segment type.
- Recovery/replacement: `f2fs_do_replace_block()` temporarily switches a curseg to the target segment, updates summary/SIT state, optionally restores the old curseg, and is used by recovery and atomic-write paths.
- Mount/build: `f2fs_build_segment_manager()` initializes flush/discard controls, SIT info, free maps, current segments, SIT entries, dirty maps, current-segment sanity checks, and GC mtime bounds.
- Zoned devices: zone reset commands replace discard for sequential zones; mount-time checks can allocate new current sections, reset empty zones, finish or zero inconsistent zones, and verify write pointers.

## Concurrency and State
- `SIT_I(sbi)->sentry_lock` protects SIT cache, valid maps, dirty SIT accounting, and checkpoint-valid counters.
- `DIRTY_I(sbi)->seglist_lock` protects dirty/pre-free/victim/pinned segment maps.
- `FREE_I(sbi)->segmap_lock` protects free segment/section maps and counters.
- Each `curseg_info` has `curseg_mutex`; `SM_I(sbi)->curseg_lock` serializes broader current-segment changes.
- Discard commands use `dcc->cmd_lock`, per-command spinlocks, completions, rb-tree/list membership, `bio_ref`, and `ref` to coordinate submit/endio/wait/removal.
- Several paths deliberately run under checkpoint, GC, or operation locks supplied by callers.

## Important Edge Cases
- F2FS bitmap bit order is reversed within bytes, so the file implements custom reverse bit search helpers for SIT/discard maps.
- Checkpoint-disabled mode tracks unusable blocks and may force SSR or reject disabling checkpoint again when unusable/free-section limits are exceeded.
- `NULL_ADDR`, `NEW_ADDR`, and `COMPRESS_ADDR` are treated specially during invalidation and allocation.
- Discard submission is skipped on corruption, unsupported devices, or io-aware busy periods; umount discard has timeout/drop behavior.
- Segment allocation failures stop checkpoint with specific reasons in non-pinning paths.
- Zoned writes require section/zone alignment; unaligned zone reset attempts return errors.
- SIT and curseg sanity checks mark corruption and require fsck on inconsistent block counts, segment types, journals, or current-segment offsets.

## Research Notes
This is the central implementation of F2FS space management. Correctness depends on tight coupling among SIT maps, free maps, dirty maps, current summaries, checkpoint state, discard state, and GC victim selection. Small changes here can affect mount recovery, fsync durability, fstrim behavior, multi-device flushing, zoned-device safety, and ENOSPC behavior.
