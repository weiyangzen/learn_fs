# File Research: sources/os/linux/linux/mm/page_isolation.c

Pageblock isolation support for memory hotplug/offline, CMA allocation, and contiguous range allocation. It marks pageblocks `MIGRATE_ISOLATE`, prevents allocator reuse of free pages in a target range, and verifies that isolated ranges have become free or otherwise acceptable.

Key responsibilities:
- Classifies pages as movable or unmovable for a requested isolation mode.
- Scans pageblocks for unmovable pages before changing migratetype to isolate.
- Sets and unsets pageblock isolation while moving free pages between normal and isolate freelists.
- Handles pageblock boundary cases where a free or in-use higher-order page crosses the isolation boundary.
- Isolates full PFN ranges with `start_isolate_page_range()` and rolls back partial isolation on failure.
- Provides `undo_isolate_page_range()` and `test_pages_isolated()` for cleanup and final verification.
- Emits page-isolation tracepoints for test results.

Important behavior:
- Reserved pages are treated as unmovable, except `ZONE_MOVABLE` lets non-reserved pages be assumed movable.
- Hugetlb pages are movable only when architecture and hstate migration support allow it; non-LRU compound pages are otherwise rejected.
- For memory offline, HWPoison and PageOffline pages are treated as acceptable special cases.
- CMA isolation may treat CMA pageblocks as movable even when ordinary isolation would not.
- Boundary isolation first handles the start and end pageblocks to avoid accounting corruption from pages spanning a pageblock boundary.
- Unisolation may isolate and put back a large buddy page to force correct merging after clearing the isolate state.

Dependencies:
- Uses pageblock flags, buddy allocator internals, zone locks, migrate types, hugetlb migration support, memory hotplug semantics, `PageOffline`, HWPoison, `page_has_movable_ops()`, and allocator helpers from `internal.h`.

Notable risks:
- The checks are explicitly approximate for LRU and movable-ops pages; callers must still migrate/free pages and then verify isolation.
- No high-level synchronization prevents overlapping isolation attempts; races are detected through already-isolated pageblocks and reported as `-EBUSY`.
- PCP pages may still exist after isolation unless callers use stronger draining or PCP disable/enable sequencing as needed.
