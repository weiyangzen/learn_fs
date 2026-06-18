# sources/storage-engines/rocksdb/db/db_impl/compacted_db_impl.h

## Purpose

`compacted_db_impl.h` declares `CompactedDBImpl`, a specialized read-only subclass of `DBImpl` for fully compacted DBs. The header documents the public contract: only read APIs are implemented, most write/maintenance APIs return `NotSupported`, and live-file enumeration is allowed without forcing a memtable flush.

## Important APIs, Types, and Members

- `CompactedDBImpl(const DBOptions&, const std::string&)`, deleted copy operations, and virtual destructor define ownership/lifetime.
- `static Status Open(const Options&, const std::string&, std::unique_ptr<DB>*)` is the construction entry point.
- `Get` and `MultiGet` override DB read APIs while exposing base overloads with `using DB::Get` and `using DB::MultiGet`.
- Mutating overrides return `Status::NotSupported`: `Put`, `PutEntity`, `Merge`, `Delete`, `Write`, `CompactRange`, `DisableFileDeletions`, `EnableFileDeletions`, `Flush`, `SyncWAL`, `IngestExternalFile`, `CreateColumnFamilyWithImport`, and `ClipColumnFamily`.
- `GetLiveFiles` delegates to `DBImpl::GetLiveFiles(..., false)` so compacted read-only mode can enumerate live files without flushing.
- Private state includes `ColumnFamilyData* cfd_`, `Version* version_`, `const Comparator* user_comparator_`, `LevelFilesBrief files_`, and `int files_level_`.

## Control Flow and Integration Contract

The header establishes that `Open` and `Init` are responsible for populating cached read state before any read call. `FindFile` is an inline private helper used by implementation reads to map a user key to a file in `files_`. All inherited write APIs that might mutate memtables, WALs, MANIFESTs, compaction state, file deletion state, or external-file state are blocked at the interface boundary.

The class is a friend of `DB`, matching other RocksDB implementation classes that are constructed through public factory functions. The TODO comments note overlap with `DBImplSecondary` and `DBImplReadOnly`, suggesting this class duplicates some read-only policy that might later be shared.

## State and Persistence Behavior

The header declares no owned persistent resources beyond the base `DBImpl` machinery. Its member pointers are non-owning references into DBImpl-managed column-family/version/super-version state. Since flush, WAL sync, writes, compaction, ingestion, import, and deletion control are disabled, this mode should not create new persistent DB files after open. Live-file listing is observational only.

## Dependencies and Integration Points

The class depends on `db/db_impl/db_impl.h` for the base implementation, `ColumnFamilyData`, `Version`, `Comparator`, and `LevelFilesBrief` declarations. It integrates with the public `DB` API by overriding methods rather than introducing a separate interface, allowing callers to hold a `std::unique_ptr<DB>` while receiving compacted-mode behavior.

## Risks and Edge Cases

Because the header blocks many but not necessarily every mutating DB API, the `FIXME` about missing write-function overrides is significant. Any inherited mutating API accidentally left enabled would violate read-only compacted-mode assumptions. The non-owning cached pointers require the implementation to preserve super-version lifetime correctly. The `GetLiveFiles` override ignores the caller's `flush_memtable` intent, which is appropriate for read-only mode but could surprise generic code expecting a flush attempt.

## Test Signals

Useful tests should assert write-like APIs return `NotSupported`, `GetLiveFiles(..., flush_memtable=true)` does not attempt a flush, open rejects unsupported DB layouts/options, and read APIs work through the normal `DB` interface despite the specialized implementation.
