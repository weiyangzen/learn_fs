# sources/storage-engines/rocksdb/db/memtable.h

## Purpose
`memtable.h` declares RocksDB's in-memory write buffer interfaces and the concrete `MemTable` implementation used before data is flushed into SST files. It separates the read-only contract (`ReadOnlyMemTable`) from the mutable `MemTable` so immutable memtables and alternate implementations, such as write-batch-with-index memtables, can be held by `MemTableList` and queried uniformly.

## Important APIs, types, and functions
`ImmutableMemTableOptions` captures the subset of immutable and mutable column-family options needed by memtables: arena sizing, prefix bloom settings, in-place update settings, merge operator, checksum protection, memory paranoia, per-key checksum verification, and batched lookup optimization.

`ReadOnlyMemTable` defines the shared interface for immutable and current memtables. Important read APIs are `NewIterator`, `NewTimestampStrippingIterator`, `NewRangeTombstoneIterator`, `NewTimestampStrippingRangeTombstoneIterator`, point `Get`, and `MultiGet`. Metadata APIs include memory usage, entry/delete/range-delete counts, `GetDataSize`, `GetFirstSequenceNumber`, `GetEarliestSequenceNumber`, `GetMinLogContainingPrepSection`, approximate stats, oldest key time, internal comparator, newest user-defined timestamp, and range tombstone cache readiness.

Flush and lifetime APIs on `ReadOnlyMemTable` include `Ref`, `Unref`, `MarkImmutable`, `MarkFlushed`, `SetID`, `SetNextLogNumber`, `GetEdits`, `SetFlushCompleted`, `SetFlushInProgress`, `SetFileNumber`, and `ReleaseFlushJobInfo`. `ProtectSealedBlobFiles` keeps direct-write blob files live until the memtable is fully unreferenced.

The concrete `MemTable` adds write APIs: `Add`, `Update`, `UpdateCallback`, `CountSuccessiveMergeEntries`, `BatchPostProcess`, dynamic `UpdateWriteBufferSize`, `RefLogContainingPrepSection`, `ShouldScheduleFlush`, `MarkFlushScheduled`, `ConstructFragmentedRangeTombstones`, `AddLogicallyRedundantRangeTombstone`, `BumpIngestSeqnoBarrier`, checksum verification, and newest-UDT tracking.

Static helpers `HandleTypeValue`, `HandleTypeDeletion`, and `HandleTypeMerge` centralize how point lookups interpret value, deletion, and merge records, including full merge invocation and raw operand collection.

## Control flow
Writes enter `MemTable::Add` or update paths, which encode internal keys into `MemTableRep`, update counters and memory estimates, optionally update prefix bloom and insert hints, and eventually mark the memtable for flush when memory/range-delete thresholds are crossed. Concurrent write batches aggregate counter deltas in `MemTablePostProcessInfo` and apply them with `BatchPostProcess`.

Point reads call `Get`, which checks range tombstones, scans the memtable representation for matching internal keys, honors snapshots and read callbacks, resolves blobs when needed, accumulates merge operands in `MergeContext`, and returns once it finds a final value, deletion, merge-in-progress boundary, or error. `MultiGet` applies the same lookup semantics over a `MultiGetContext::Range`.

When a mutable memtable is sealed, higher layers call `ConstructFragmentedRangeTombstones` and `MarkImmutable`; future reads can then reuse fragmented range tombstone structures. Flush code consumes iterators and `VersionEdit` metadata, then calls `MarkFlushed` after persistence is installed.

## State and persistence behavior
This header defines only in-memory structures, but it carries persistence metadata: `VersionEdit edit_`, `mem_next_walfile_number_`, `file_number_`, `atomic_flush_seqno_`, and `flush_job_info_`. These fields bridge the mutable write buffer to MANIFEST edits, WAL retention, atomic flush boundaries, and flush event reporting.

Memory state is tracked through `ConcurrentArena`, `AllocTracker`, table/range-delete reps, `DynamicBloom`, approximate memory counters, and mutable write-buffer size. Sequence state includes first sequence, earliest sequence, creation sequence, ingest barrier sequence, and the minimum WAL containing a prepared transaction section. User-defined timestamp state is stored as an atomic pointer into arena-owned key memory.

## Dependencies and integration points
`MemTable` integrates with `dbformat`, merge logic, range tombstone fragmentation, read callbacks, sequence-to-time mapping, version edits, allocators, concurrent arena, RocksDB options, `MemTableRep`, MultiGet, blob fetchers/partition managers, wide columns, and write-buffer management. `MemTableList` depends on this interface for immutable memtable lifecycle, reads, flush selection, history retention, and WAL recovery edits.

## Risks and edge cases
Most APIs require external synchronization unless the memtable is immutable; violating that contract risks use-after-free, stale range tombstone caches, or inconsistent counters. Merge handling is sensitive to operand order and whether the caller wants merged values or raw operands. Range tombstone conversion must respect the ingest sequence barrier to avoid shadowing newly ingested L0 data. Blob file protection must outlive column-family metadata. User-defined timestamp tracking depends on arena lifetime and atomic max updates.

## Test signals
Relevant coverage comes from `memtable_list_test.cc` for list-level point reads, history retention, flush lifecycle, and newest UDT queries; `merge_helper_test.cc` and `merge_test.cc` for merge semantics used by lookup helpers; and broader RocksDB memtable, write, flush, transaction, blob, timestamp, and range deletion tests.
