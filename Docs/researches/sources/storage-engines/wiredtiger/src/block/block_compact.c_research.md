# sources/storage-engines/wiredtiger/src/block/block_compact.c

## Purpose
This file implements block-manager compaction decisions, progress estimation, page rewrite support, and verbose file-space diagnostics.

## Important APIs, Types, and Functions
Entry points are `__wt_block_compact_start`, `__wt_block_compact_end`, `__wt_block_compact_get_progress_stats`, `__wt_block_compact_skip`, `__wt_block_compact_page_skip`, `__wt_block_compact_page_rewrite`, and `__wt_block_compact_progress`. Helpers include extent trimming, skip heuristics, remaining-work estimation, page-level skip checks, and verbose bucket dumps.

## Control Flow
Start rejects concurrent compaction, switches to first-fit allocation, resets counters, records the session, and notifies background compaction. Skip logic ignores small files, checks configured free-space targets, stops if the file grew, and requires enough free space in the first 80 or 90 percent to move pages out of the last 20 or 10 percent. Page rewrite reads the old block, allocates a replacement earlier in the file, writes unchanged bytes, frees the old extent, repacks the address cookie, and updates stats.

## State and Persistence Behavior
Compaction changes persistent block layout by moving pages and freeing old extents. `WT_BLOCK` stores reviewed/rewritten/skipped counters, expected work, selected compaction percentage, previous file size, and owning session. Dry run estimates work and cancels without rewriting.

## Dependencies and Integration Points
The file depends on address-cookie helpers, block allocation/free/read/write, live extent lists, compact session config, background compaction hooks, stats, verbose logging, and `live_lock`. Higher btree compaction traversal calls it per page.

## Risks and Edge Cases
Heuristics can skip when concurrent file growth occurs. Estimation assumes reviewed pages are representative. Rewrite counters are updated before the rewrite fully succeeds, so they are progress counters. The rewrite preserves the original checksum because bytes are unchanged.

## Test Signals
Tests should cover thresholds, sub-1 MiB files, free-space target behavior, dry run, no-progress skip, successful rewrite/address update, allocation-failure cleanup, background hooks, progress stats, and verbose file-space buckets.
