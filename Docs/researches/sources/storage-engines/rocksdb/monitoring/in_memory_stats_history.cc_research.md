# sources/storage-engines/rocksdb/monitoring/in_memory_stats_history.cc

Purpose: Implements an iterator over DB statistics snapshots retained in `DBImpl` memory.

Important APIs/types/functions: `InMemoryStatsHistoryIterator::~InMemoryStatsHistoryIterator`, `Valid`, `status`, `Next`, `GetStatsTime`, `GetStatsMap`, and private `AdvanceIteratorByTime`.

Control flow: Construction calls `AdvanceIteratorByTime(start_time_, end_time_)`. `Next` calls `AdvanceIteratorByTime(GetStatsTime() + 1, end_time_)` to avoid returning the same timestamp repeatedly. `AdvanceIteratorByTime` delegates to `DBImpl::FindStatsByTime`, which fills the next timestamp and copied stats map; a null DB pointer invalidates the iterator.

State and persistence behavior: The iterator stores a copy of the current stats map, making the current result stable even if DBImpl garbage-collects old in-memory snapshots. It does not persist data; it reflects the in-memory history buffer only.

Dependencies/integration: Depends on `db/db_impl/db_impl.h` and the public `StatsHistoryIterator` interface. Created by DB stats-history APIs when persistent stats are not used.

Risks/test signals: Long gaps between `Next` calls may skip purged snapshots, as documented in the header. `stats_history_test.cc` covers in-memory retrieval and buffer-size purging behavior.
