# File Research: sources/os/linux/linux/fs/f2fs/segment.h

Read completely: 1052 lines.

## Purpose
Defines the F2FS segment-manager data model, address/segment conversion macros, allocation/GC mode constants, dirty-segment types, SIT/free/dirty/curseg structures, and inline helpers used by `segment.c`, GC, checkpoint, data writeback, and node management.

## Main Responsibilities
- Converts among block addresses, logical/relative segment numbers, sections, zones, SIT blocks, and summary blocks.
- Defines LFS, SSR, AT_SSR, GC, foreground/background GC, and dirty segment classifications.
- Describes in-memory SIT state through `seg_entry`, `sec_entry`, `sit_info`, and `sit_entry_set`.
- Describes segment allocation state through `free_segmap_info`, `dirty_seglist_info`, and `curseg_info`.
- Provides fast inline accessors for current segments, valid block counts, free/dirty/pre-free counts, overprovisioning, utilization, and checkpoint readiness.
- Provides SIT serialization/deserialization helpers and SIT block address flipping.
- Encodes IPU policy flags and helpers.
- Provides writeback sizing hints and discard-thread wakeup logic.

## Key Definitions
- Address macros: `MAIN_BLKADDR`, `SEG0_BLKADDR`, `START_BLOCK`, `NEXT_FREE_BLKADDR`, `GET_SEGNO`, `GET_SEC_FROM_SEG`, `GET_ZONE_FROM_SEG`, `GET_SUM_BLOCK`, and `SUM_BLK_PAGE_ADDR`.
- Capacity macros: `CAP_BLKS_PER_SEC` and `CAP_SEGS_PER_SEC` account for zoned-device unusable zone capacity.
- `victim_sel_policy` carries GC/SSR selection inputs such as dirty bitmap, search bounds, min cost, age, and age threshold.
- `seg_entry` stores segment type, valid counts, current/checkpoint valid maps, optional mirror map, discard map, and modification time.
- `sit_info` stores SIT block addresses, bitmaps, dirty SIT tracking, segment/section entry arrays, and mtime bounds for cost-benefit GC.
- `free_segmap_info` tracks free segments/sections and their bitmaps.
- `dirty_seglist_info` tracks type-specific dirty maps, generic dirty/pre-free maps, dirty section map, victim map, and pinned section map.
- `curseg_info` tracks active log state: summary block, journal, allocation type, segment type, current segment, next block offset, zone, pending next segment, and fragmentation mode state.

## Key Inline Behavior
- `get_valid_blocks()` and `get_ckpt_valid_blocks()` return segment-level or section-level counts depending on large-section mode.
- `set_ckpt_valid_blocks()` and `sanity_check_valid_blocks()` synchronize/check section checkpoint-valid counters from segment entries.
- `seg_info_from_raw_sit()`, `seg_info_to_raw_sit()`, and `seg_info_to_sit_folio()` translate between raw on-disk SIT entries and in-memory entries.
- `__set_free()`, `__set_inuse()`, `__set_test_and_free()`, and `__set_test_and_inuse()` update free segment and free section maps with counter maintenance.
- `__get_secs_required()`, `has_not_enough_free_secs()`, and `f2fs_is_checkpoint_ready()` estimate free-section requirements from dirty node/dentry/imeta/data pages and reserved sections.
- `check_block_count()` validates raw SIT valid-block count against the valid bitmap and usable segment capacity, marking the filesystem for fsck on mismatch.
- `current_sit_addr()`, `next_sit_addr()`, and `set_to_next_sit()` implement SIT double-buffering.
- `get_mtime()` computes filesystem-relative elapsed time for GC aging.
- `nr_pages_to_skip()` and `nr_pages_to_write()` bias writeback toward segment-sized or bio-sized batching.
- `wake_up_discard_thread()` wakes the discard thread only when pending requests meet granularity or a force wake is requested.

## Concurrency and Assumptions
Many helpers directly mutate shared counters and bitmaps and assume callers hold the documented locks from `segment.c`: free segmap spinlock, dirty seglist mutex, SIT sentry rwsem, current-segment locks, or checkpoint/GC locks. The header prioritizes fast inline operations over defensive locking.

## Important Edge Cases
- `GET_SEGNO()` returns `NULL_SEGNO` for invalid/non-data block addresses.
- Zoned-device capacity can make part of a segment unusable, so valid-block checks use `f2fs_usable_blks_in_seg()`.
- Free section accounting excludes current sections in some in-memory log transitions.
- Active log count changes how dentry/data dirty-page requirements are separated.
- SIT bitmap mirror checks are enabled under `CONFIG_F2FS_CHECK_FS`.
