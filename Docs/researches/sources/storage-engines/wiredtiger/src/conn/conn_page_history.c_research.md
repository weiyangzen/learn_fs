# sources/storage-engines/wiredtiger/src/conn/conn_page_history.c

## Purpose
This file implements debug-mode page history tracking. When enabled, it records read and eviction counts for pages with disaggregated page IDs and periodically reports the most reread and most evicted pages.

## Important APIs, Types, and Functions
Public entry points are `__wti_conn_page_history_config`, `__wti_conn_page_history_destroy`, `__wt_conn_page_history_track_evict`, and `__wt_conn_page_history_track_read`. Local helpers include report formatting, top-N comparators, `__conn_page_history_report`, and the reporter thread `__conn_page_history_reporter`. Key types are `WT_PAGE_HISTORY`, `WT_PAGE_HISTORY_ITEM`, `WT_PAGE_HISTORY_KEY`, and `WT_HASH_MAP`.

## Control Flow and Behavior
Configuration reads `debug_mode.page_history`. Enabling lazily initializes a large hash map, allocates a condition variable, opens a dedicated internal session, clears shutdown, and starts a reporter thread. Disabling stops the reporter but intentionally keeps the rest of the state alive to avoid synchronization hazards with concurrent track calls.

Track-read increments global read counters, ignores local pages without disaggregated info, keys pages by table ID and page ID, records first/last read timestamps and global read counters, increments per-page reads, and increments reread count after the first read. Track-evict similarly counts global, local, and no-page-ID evictions and increments per-page eviction counts. The reporter wakes every second and emits a report every 30 wakeups, scanning the hash map under bucket locks and maintaining top-five arrays for reads and evictions.

## State and Persistence
All state is in memory and debug-only. It tracks global read/evict counters, local/no-page-ID counters, rereads, a hash map of page history items, reporter session/thread/condition state, and shutdown/enabled flags. It does not persist page history across restarts.

## Dependencies and Integration Points
The tracker depends on disaggregated page IDs in `page->disagg_info`, btree table IDs from `S2BT(session)->id`, hash-map locking, atomics/barriers, internal sessions, and connection verbose/message output. It is configured during worker startup and reconfiguration, and destroyed early in connection close.

## Risks
Risks include high memory use from a 10-million-entry hash map, overhead on every tracked read/evict, races when disabling while sessions are still tracking, relying on disaggregated page IDs only, and report sorting while holding hash bucket locks. The code keeps state alive after disable specifically to reduce use-after-free risk.

## Test Signals
Signals include debug-mode configuration tests, periodic report output, counters for local versus disaggregated pages, top-N output correctness, clean thread shutdown on reconfigure/close, and stress tests that read/evict pages while toggling the feature.
