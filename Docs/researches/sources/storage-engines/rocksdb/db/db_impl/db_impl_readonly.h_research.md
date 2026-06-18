# sources/storage-engines/rocksdb/db/db_impl/db_impl_readonly.h

## Purpose

`db_impl_readonly.h` declares `DBImplReadOnly`, the DBImpl subclass used for ordinary read-only opens. It exposes read operations, blocks mutating DB APIs, and provides the helper used by public `DB::OpenForReadOnly` overloads.

## Important APIs, Types, And Functions

- `class DBImplReadOnly : public DBImpl` inherits most read infrastructure from DBImpl.
- Constructor `DBImplReadOnly(const DBOptions&, const std::string&)` and deleted copy/assignment enforce normal DB object ownership.
- `GetImpl`, `NewIterator`, and `NewIterators` are overridden to provide read-only read paths.
- Mutating APIs including `Put`, `PutEntity`, `Merge`, `Delete`, `SingleDelete`, `Write`, `CompactRange`, `CompactFiles`, file-deletion controls, `Flush`, `SyncWAL`, `FlushWAL`, external-file ingestion, import, clipping, and column-family creation all return `Status::NotSupported("Not supported operation in read only mode.")`.
- `GetLiveFiles` delegates to `DBImpl::GetLiveFiles` with `flush_memtable=false`, ignoring the caller flush flag.
- `FlushForGetLiveFiles` is overridden as a no-op.
- Private static `OpenForReadOnlyWithoutCheck` centralizes construction/recovery after caller-side existence checks.

## Control Flow

The public DB API routes read-only opens through friend class `DB`, which calls `OpenForReadOnlyWithoutCheck`. Once constructed and recovered, read APIs use the overrides declared here. Write-like APIs fail immediately before they can schedule WAL writes, flushes, compactions, ingestion, metadata updates, or column-family mutations.

## State And Persistence Behavior

The class is designed to avoid persistent mutation. It does not allow writes, WAL sync/flush, manual flush, compaction, ingestion, CF creation, or file deletion toggling. Live-file listing is read-only because memtable flushing is suppressed. Recovery still builds in-memory state and may read WALs to expose the latest persisted data, but the class does not publish new recovery metadata.

## Dependencies And Integration Points

The header depends on `DBImpl` and public RocksDB API types such as `WriteOptions`, `ReadOptions`, `ColumnFamilyHandle`, `Iterator`, compaction options, external-file ingestion types, and import metadata. It integrates with `db_impl_readonly.cc` for read paths and with public `DB::OpenForReadOnly` overloads through the `friend class DB` declaration.

## Risks And Edge Cases

- New mutating DB APIs added to the base class can bypass read-only restrictions unless this class is updated; the header includes a FIXME noting missing write-function overrides.
- `GetLiveFiles` intentionally ignores a caller request to flush; tests should ensure this behavior is not mistaken for a successful flush.
- Public overload hiding is managed with `using` declarations; missing `using` entries can accidentally hide base overloads or change API availability.
- Returning `NotSupported` is the safety contract, so status text/behavior consistency matters for callers that branch on read-only failures.

## Test Signals

Compile/API tests should verify all mutating methods return `NotSupported` in read-only mode, while read methods remain available. Regression tests should check that adding new DB write APIs requires read-only overrides, `GetLiveFiles` never flushes, `FlushForGetLiveFiles` is a no-op, and public overload resolution continues to select the intended read-only methods.
