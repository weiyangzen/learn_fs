# sources/storage-engines/rocksdb/monitoring/persistent_stats_history.cc

Purpose: Implements persistent stats-history key/version helpers and an iterator over the persistent stats column family.

Important APIs/types/functions: Defines version-key strings and current/compatible versions. `DecodePersistentStatsVersionNumber` reads version metadata from the persistent stats CF. `EncodePersistentStatsKey` formats keys as zero-padded seconds timestamp plus `#` plus stats key. `OptimizeForPersistentStats` tunes CF options. `PersistentStatsHistoryIterator` implements `Valid`, `status`, `Next`, `GetStatsTime`, `GetStatsMap`, and `AdvanceIteratorByTime`. Local `parseKey` decodes persisted keys.

Control flow: The iterator seeks the persistent stats CF to the starting timestamp string, parses the first timestamp at or after the requested start, invalidates if beyond end time, then scans all entries with the same timestamp into a map while skipping format-version keys.

State and persistence behavior: Persistent history lives in a RocksDB column family. Iterator state stores current timestamp, bounds, stats map, status, valid flag, and raw `DBImpl*`. Key format sorts by time because timestamps are fixed width.

Dependencies/integration: Depends on `DBImpl`, persistent stats CF accessors, `ReadOptions`, iterators, and `ParseUint64`.

Risks/test signals: `EncodePersistentStatsKey` casts timestamps to `int` for `%010d`, limiting useful range despite `uint64_t` API. `parseKey` returns max timestamp for malformed/too-old keys; iterator logic can then invalidate. Tests cover disk retrieval, reopen recovery, values, read-only, and CF interactions.
