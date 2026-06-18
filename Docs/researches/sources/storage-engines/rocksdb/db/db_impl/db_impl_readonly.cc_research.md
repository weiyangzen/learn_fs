# sources/storage-engines/rocksdb/db/db_impl/db_impl_readonly.cc

## Purpose

`db_impl_readonly.cc` implements the read-only DB variant. It opens a DB without write ownership, supports point lookups and iterators over recovered versions/memtables, rejects write APIs in the header, and exposes `DB::OpenForReadOnly` entry points. It reuses normal DBImpl recovery in read-only mode but avoids creating writable WALs, flushing, compaction, or file-deletion state changes.

## Important APIs, Types, And Functions

- `DBImplReadOnly::DBImplReadOnly` constructs `DBImpl` with `read_only=true`, `seq_per_batch=false`, and `batch_per_txn=true`.
- `DBImplReadOnly::GetImpl` implements read-only `Get` with timestamp validation, memtable/table lookup, merge handling, optional blob resolution for memtable blob references, and read statistics.
- `DBImplReadOnly::NewIterator` creates a single-CF arena-wrapped DB iterator over a referenced superversion.
- `DBImplReadOnly::NewIterators` creates multiple CF iterators with shared read sequence and carefully unreferences already-acquired superversions on validation failure.
- `OpenForReadOnlyCheckExistence` checks `CURRENT`/MANIFEST existence or creates the directory under historical `create_if_missing` behavior.
- `DB::OpenForReadOnly` overloads handle default-CF and multi-CF open, including a fast attempt to open a fully compacted DB through `CompactedDBImpl::Open`.
- `DBImplReadOnly::OpenForReadOnlyWithoutCheck` constructs the read-only impl, recovers with `read_only=true`, creates handles, installs superversions, marks open success, and optionally schedules async file opening.

## Control Flow

Default-CF `DB::OpenForReadOnly` first checks existence, clears `dbptr`, tries `CompactedDBImpl::Open`, and if that fails builds default column-family descriptors and calls `OpenForReadOnlyWithoutCheck`. The multi-CF overload performs the same existence check and delegates directly.

`OpenForReadOnlyWithoutCheck` clears output handles, creates `DBImplReadOnly`, locks the DB mutex, calls base `Recover(column_families, true, error_if_wal_file_exists)`, validates that requested CFs exist, creates `ColumnFamilyHandleImpl` objects, installs superversions for every recovered CF, sets `opened_successfully_`, schedules async table-file opening if requested, unlocks, cleans the `SuperVersionContext`, and either publishes the DB or deletes handles/impl on failure.

`GetImpl` validates timestamp usage against CF comparator settings, clears output timestamp storage, sets a snapshot sequence to `versions_->LastSequence()`, builds a timestamp read callback, traces the get if tracing is enabled, obtains the current superversion without ref/unref overhead, checks collapsed-history constraints for timestamp reads, probes mutable memtable first, postprocesses blob-backed memtable values when necessary, otherwise probes the current version's files, and records key/byte/perf counters. It supports returning values, wide columns, or merge operands.

`NewIterator` validates `ReadOptions::io_activity`, normalizes unknown activity to `kDBIterator`, validates timestamp settings and collapsed-history constraints, refs the current superversion, chooses the explicit snapshot sequence or last sequence, and creates an arena-wrapped DB iterator with refresh and memtable-flush marking disabled. `NewIterators` applies the same checks across CFs, refs all superversions before constructing iterators, and unwinds refs on failure.

## State And Persistence Behavior

Read-only open reads MANIFEST, WAL files if recovery requires them, and OPTIONS metadata, but it does not create a new WAL or write recovery edits. The base recovery path updates in-memory `versions_`, memtables, `options_file_number_`, handles, and superversions. `GetImpl` reads at `LastSequence()` rather than installing a DB snapshot. Iterators hold superversion references so files/memtables remain alive while the iterator exists. `FlushForGetLiveFiles` is a no-op in the header so live-file listing does not attempt a read-only flush.

## Dependencies And Integration Points

This file depends on normal DBImpl recovery/open infrastructure, `CompactedDBImpl`, column-family handles, superversions, memtables, `Version::Get`, merge context, blob fetcher/cache, timestamp/collapsed-history validation helpers, tracing/perf counters, and async table opening from `db_impl_open.cc`. It is the implementation behind the public `DB::OpenForReadOnly` API.

## Risks And Edge Cases

- `GetImpl` intentionally avoids normal superversion ref/unref for read-only mode; that assumes no background writes/compactions will swap state underneath it.
- Timestamp validation must reject reads without timestamps on timestamp-enabled CFs and mismatched timestamp sizes.
- Read-only recovery with `error_if_wal_file_exists` must detect non-empty WALs to avoid silently exposing unflushed data when the caller asked for strictness.
- Blob-backed memtable values can exist after recovery or option changes, so blob fetcher setup must account for both direct-write and blob-file settings.
- Multi-iterator creation must release all acquired superversion refs if any CF fails collapsed-history validation.
- The fully compacted fast path changes which implementation backs `DB::OpenForReadOnly`, so behavior should remain API-compatible.

## Test Signals

Useful tests include read-only point gets from memtable and SST, merge operand reads, wide-column/entity reads, timestamp-enabled CF reads and collapsed-history failures, blob-backed recovered memtable values, iterator and multi-iterator lifetime/ref cleanup, `io_activity` validation, default and multi-CF open, missing CF errors, `create_if_missing` historical behavior, non-empty WAL rejection with `error_if_wal_file_exists`, async file opening in read-only mode, and fallback from `CompactedDBImpl::Open` to `DBImplReadOnly`.
