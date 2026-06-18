<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/wtcache.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/runner/wtcache.py

Purpose: emits a focused snapshot of WiredTiger cache and eviction statistics for Workgen cache workloads.

Important APIs and functions: public `get_cache_eviction_stats(session, cache_eviction_file)`. It reads `wiredtiger.stat.conn` counters for cache bytes, history store bytes, eviction trigger hits, app reads/writes, app eviction attempts/failures, forced eviction, and eviction worker attempts/failures.

Control flow: open append file or use stdout; open a `statistics:` cursor; print a start marker; compute percentages relative to `cache_bytes_max`; print cache occupancy, history store occupancy, trigger counters, app page counters, app eviction counters, forced eviction counters, worker eviction counters; close cursor.

State and persistence: appends to the given stats file, commonly `cache_eviction.stat`, or writes stdout. It does not mutate database state.

Dependencies and integration: imported by `runner.__init__`; used by `cache_workload_update_trigger.py` and likely similar cache workloads.

Risks: divides by `cache_total`, so a zero/unavailable cache max would fail. File handle is not explicitly closed. Imports `json` but does not use it. Some counters depend on WiredTiger stat names and may break across versions.

Test signals: cache stats file with start/end markers and populated counter values.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/runner/wtcache.py -->
