# sources/storage-engines/rocksdb/db/db_secondary_test.cc

## Purpose

This file tests RocksDB secondary-instance behavior: opening a primary DB as a secondary, catching up from MANIFEST/WAL changes, secondary-side compaction service flows, timestamped secondary reads, blob-backed entity resolution, column-family handling, live-file reporting, and failure handling around missing files or inconsistent versions.

## Important APIs, Types, And Functions

- `DBSecondaryTestBase` derives from `DBBasicTestWithTimestampBase` and owns `secondary_path_`, `handles_secondary_`, and `db_secondary_`.
- Helpers include `ReopenAsSecondary`, `TryOpenSecondary`, `OpenSecondary`, `OpenSecondaryWithColumnFamilies`, `CloseSecondary`, `db_secondary_full()`, and `CheckFileTypeCounts`.
- Core APIs include `DB::OpenAsSecondary`, `DB::TryCatchUpWithPrimary`, `DBImplSecondary::TEST_CompactWithoutInstallation`, `DB::OpenAndCompact`, `DB::GetLiveFiles`, `DBImpl::GetImpl`, `GetMergeOperands`, `GetEntity`, `PutEntity`, `PutBlobIndex`, and `TransactionDB::Open`.
- Test-specific helpers include `TraceFileEnv`, SyncPoint callbacks/dependencies, `CompactionServiceInput`, `CompactionServiceResult`, `WideColumns`, `BlobIndex`, and merge operators.

## Control Flow

The opening tests cover logger creation failures, nonexistent primaries, reopening a closed DB as secondary, and reading normal values plus wide-column entities through a secondary iterator. Internal compaction tests create L0/L1/L2 input files, build `CompactionServiceInput`, open a secondary with `max_open_files = -1`, and run `TEST_CompactWithoutInstallation`, checking output file metadata, bytes written, levels, output path, and invalid-argument behavior when files are missing or already compacted.

Read-path tests verify merge operands, blob-backed V2 entity base values in SST plus newer merge operands from catch-up, raw blob-index return through internal `GetImpl`, direct-write blob entity resolution after WAL catch-up, and `kBlockCacheTier` returning `Incomplete` instead of issuing blob I/O. Standard secondary catch-up tests write/flush/compact on the primary, call `TryCatchUpWithPrimary`, and verify `Get` and iterator views. WAL-tail tests ensure the secondary keeps tailing the current WAL even when a higher-number empty WAL exists and that repeated catch-up is stable.

MANIFEST and file-lifecycle tests exercise opening while the primary switches manifests, catching up across manifest switches, missing table files during open versus after open, primary column-family drops, opening subsets of column families, and unsupported dynamic `max_open_files` changes on secondary. Disabled WAL-switch tests document intended behavior but are not active.

The timestamp section mirrors the read-only timestamp file, but reopens with `ReopenAsSecondary` instead of `ReadOnlyReopen`. It checks invalid read timestamp size, read timestamp without write timestamps, read without timestamp over timestamped data, full-history-low sanity failures, and positive iterator/Get/NewIterators behavior.

## State And Persistence Behavior

The primary DB owns durable WAL, SST, CURRENT, MANIFEST, OPTIONS, blob files, and column-family metadata. The secondary maintains its own secondary path while reading primary files and tailing primary metadata/logs. Catch-up refreshes secondary versions and memtables without accepting direct writes through the secondary. Compaction-service tests produce output under `secondary_path_` without installing it into the primary. Blob and wide-column tests rely on persisted SST blob references plus WAL-replayed memtable entries.

## Dependencies And Integration Points

This file reaches into secondary implementation internals via `db_impl_secondary.h`, regular DB internals via `DBImpl`, filename parsing, write-batch internals, blob index encoding, wide-column helpers, transaction DB, string-append merge operators, and SyncPoint scheduling. It also integrates with timestamp utilities, compaction service serialization/options override, file cache closure, live-file enumeration, and corruption/status propagation from `VersionBuilder`.

## Risks And Edge Cases

Secondary DB correctness is sensitive to races with primary manifest rollover, WAL numbering, precreated future WALs, missing or compacted-away table files, and column-family changes. Tests that use `max_open_files = -1` assume all relevant table readers are loaded. Blob direct-write tests distinguish resolving blob values from exposing encoded blob indexes, and the block-cache-tier test prevents accidental I/O. SyncPoint-driven tests can become brittle if internal point names move.

## Test Signals

Signals include exact status classes (`OK`, `IOError`, `TryAgain`, `InvalidArgument`, `Corruption`, `Incomplete`, `NotSupported`), primary/secondary `Get` and iterator value equality, output compaction metadata, file-type counts, SyncPoint-observed option overrides, file-close counters, live-file list contents and growth, timestamped entry checks, and blob/wide-column equality assertions.
