# sources/storage-engines/rocksdb/monitoring/persistent_stats_history.h

Purpose: Declares persistent stats-history metadata helpers and the `StatsHistoryIterator` implementation for the persistent stats column family.

Important APIs/types/functions: Extern strings/version constants name format and compatibility keys. `StatsVersionKeyType` selects version key type. Declares `DecodePersistentStatsVersionNumber`, `EncodePersistentStatsKey`, `OptimizeForPersistentStats`, and `PersistentStatsHistoryIterator`.

Control flow/integration: DB open/persist paths use the helpers to configure and validate the persistent stats CF. DB stats-history APIs can return `PersistentStatsHistoryIterator` to scan time-bounded persisted snapshots.

State and persistence behavior: The iterator stores current time, requested bounds, copied stats map, status, valid flag, and non-owning `DBImpl*`. Actual stats are persisted as key/value pairs in a dedicated column family.

Dependencies: Includes `db/db_impl/db_impl.h` and `rocksdb/stats_history.h`.

Risks/test signals: Copy/move are deleted to prevent accidental duplication of iterator state and raw DB pointer. Header comments contain a typo (`persitent`) but document the version-read contract. `stats_history_test.cc` provides integration coverage.
