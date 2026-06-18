<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/wal_filter.h -->
# Research: sources/storage-engines/rocksdb/include/rocksdb/wal_filter.h

Purpose: Defines `WalFilter`, a customizable recovery hook that lets applications inspect, modify, skip, stop, or reject WAL records during replay. It is a public extension point for recovery-time policy and migration logic.

Important APIs/types/functions: `WalFilter::Type`, `CreateFromString`, `WalProcessingOption`, `ColumnFamilyLogNumberMap`, `LogRecordFound`, legacy `LogRecord`, and pure virtual `Name` are the key surface. `WalProcessingOption` distinguishes continue, ignore current record, stop replay/discard later logs, and corrupted record.

Control flow: During recovery, RocksDB can first provide column-family log-number/name-id maps, then calls `LogRecordFound` for each WAL record with log metadata, the original `WriteBatch`, an optional replacement batch, and a `batch_changed` flag. The default `LogRecordFound` delegates to the older `LogRecord` overload for compatibility.

State and persistence behavior: The filter does not persist state itself, but its return value directly affects recovered DB state. `kIgnoreCurrentRecord` skips one batch; `kStopReplay` discards logs from the current record onward; a replacement batch changes replayed contents and must not contain more records than the original.

Dependencies and integration points: Inherits `Customizable`, uses `ConfigOptions`, `WriteBatch`, and column-family id/name maps. It integrates with DB recovery, configuration string parsing, WAL replay, and logging through `Name`.

Risks and edge cases: Exceptions must not escape into RocksDB because the code is not exception-safe. Returning a replacement batch with too many records fails recovery. Incorrect log-number/column-family filtering can silently drop required data or replay stale records.

Test signals: `WalFilterTest`, `WALRecoveryModeTest`, and recovery tests should verify skip/stop/corruption behavior, replacement batches, column-family log-number routing, and the legacy `LogRecord` fallback path.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/include/rocksdb/wal_filter.h -->
