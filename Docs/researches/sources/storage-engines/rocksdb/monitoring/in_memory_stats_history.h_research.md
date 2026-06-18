# sources/storage-engines/rocksdb/monitoring/in_memory_stats_history.h

Purpose: Declares `InMemoryStatsHistoryIterator`, the `StatsHistoryIterator` implementation for DBImpl's in-memory stats-history map.

Important APIs/types/functions: Constructor accepts `[start_time, end_time)` and `DBImpl*`, then positions the iterator. Public API implements `Valid`, `status`, `Next`, `GetStatsTime`, and `GetStatsMap`. Copy and move operations are deleted.

Control flow/integration: The iterator advances by timestamp range and copies the pointed snapshot into `stats_map_`. This copy is the key integration contract with `DBImpl::stats_history_` garbage collection: the current snapshot survives after the DB's backing map has purged it.

State and persistence behavior: Fields track current `time_`, requested time bounds, copied `stats_map_`, `status_`, `valid_`, and raw `DBImpl*`. It has no ownership of the DB and no disk persistence.

Dependencies: Depends on `rocksdb/stats_history.h` and forward knowledge of `DBImpl`.

Risks/test signals: The raw DB pointer must outlive the iterator. Comments note possible fragmented segments when callers wait too long between `Next()` calls and GC interleaves. DB tests validate snapshot access and purging.
