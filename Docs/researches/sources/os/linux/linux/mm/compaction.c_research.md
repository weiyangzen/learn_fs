# File Research: sources/os/linux/linux/mm/compaction.c

Linux memory compaction implementation for reducing external fragmentation by migrating movable pages out of lower PFN pageblocks and freeing higher PFN pageblocks for high-order allocations, CMA, huge pages, and proactive background compaction.

Key responsibilities:
- Maintains per-zone compaction deferral state (`compact_considered`, `compact_defer_shift`, `compact_order_failed`) to avoid repeated expensive attempts after failures.
- Tracks pageblock skip hints and cached scanner PFNs so future compaction can avoid recently unsuitable pageblocks.
- Implements free-page isolation (`isolate_freepages_block()`, `isolate_freepages_range()`) and migration-source isolation (`isolate_migratepages_block()`, `isolate_migratepages_range()`).
- Runs the main two-ended scanner in `compact_zone()`: migration scanner moves upward, free scanner moves downward, with completion when scanners meet or allocation success is predicted.
- Provides direct allocation path entry point `try_to_compact_pages()` and node-wide/manual paths through `compact_node()` / `compact_nodes()`.
- Implements `/proc/sys/vm/compact_memory`, `compaction_proactiveness`, `extfrag_threshold`, and `compact_unevictable_allowed` sysctls.
- Implements NUMA node sysfs compaction hook and background `kcompactd` worker lifecycle.

Important flows:
- `compact_zone_order()` builds a `compact_control`, installs `current->capture_control`, runs `compact_zone()`, then reports captured pages.
- `compact_finished()` checks scanner convergence, proactive fragmentation thresholds, pageblock alignment, free-area availability, fallback suitability, and contention.
- `compaction_suitable()` combines watermark checks with fragmentation index heuristics to decide whether compaction is worth attempting.
- `kcompactd()` sleeps on node waitqueues, handles allocation-triggered work via `kcompactd_do_work()`, and periodically performs proactive compaction based on weighted node fragmentation scores.
- `wakeup_kcompactd()` records the highest requested order and highest zone index, then wakes the daemon only if the node is currently suitable.

Concurrency and correctness notes:
- Uses zone locks, lruvec locks, RCU read sections, fatal-signal checks, and periodic `cond_resched()` to balance correctness and latency.
- Async compaction uses trylock-style contention detection and aborts more readily than sync/light sync paths.
- Strict free isolation is used by contiguous allocation/CMA-style callers and rolls back if any PFN in the requested range is invalid or non-free.
- Compound, THP, hugetlb, buddy, LRU, movable-ops, dirty/writeback, pinned, unevictable, and inaccessible mapping cases are handled separately during isolation.
- PCP/LRU drain points are used after migration to let freed pages merge before allocation success is tested.
