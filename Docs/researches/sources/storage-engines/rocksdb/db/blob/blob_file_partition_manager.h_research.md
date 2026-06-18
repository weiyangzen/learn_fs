<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_partition_manager.h -->
# sources/storage-engines/rocksdb/db/blob/blob_file_partition_manager.h

## Purpose
Declares the per-column-family manager for write-path blob direct write. The interface documents how active partition writers, immutable memtable generations, sealed file additions, initial garbage, and direct-write read fallback are coordinated.

## Important APIs, Types, and Functions
The public API includes `WriteBlob`, `SelectWideColumnPartition`, `RotateCurrentGeneration`, `PrepareFlushAdditions`, `CommitPreparedGenerations`, `SyncAllOpenFiles`, file-number protection/query helpers, rollback garbage marking, and static `ResolveBlobDirectWriteIndex`. Internal structs model lifecycle state: `Partition` for active writers, `DeferredFile` for writers moved out at memtable rotation, `SealedFile` for manifest-ready metadata plus initial garbage, and `GenerationBatch` for FIFO immutable memtable batches.

## Control Flow
The header defines a two-phase lifecycle: active partition writes are either sealed during the mutable generation or deferred at memtable switch; flush preparation seals deferred writers and exposes additions; commit removes prepared generations only after MANIFEST edits land. File-number tracking uses a separate RW mutex so obsolete-file and read paths can query ownership without taking the main append-generation mutex.

## State and Persistence Behavior
State includes writer ownership, file size, blob counts, total record bytes, compression and column-family identity, sync requirements, initial garbage counters, current-generation sealed files, queued immutable generations, manager-owned file mappings, and protected sealed-file reference counts. Persistent state is not directly edited by this header, but the exported `BlobFileAddition` and `BlobFileGarbage` vectors are the contract used by flush/version code to publish blob files.

## Dependencies and Integration Points
The declaration ties together blob additions, garbage records, log writer, blob file cache, callbacks, listeners, checksum factories, IO tracer, RocksDB options, wide-column partition strategy, `Version`, and read-prefetch/pinnable-slice APIs. It sits between write batch transformation, memtable/flush scheduling, MANIFEST publication, blob cache lifecycle, and read paths that encounter direct-write blob indexes.

## Risks and Edge Cases
The documented v1 design still serializes blob appends through one manager mutex, so partition fanout does not yet imply fully parallel blob file writes. Callers must respect generation ordering and pair `PrepareFlushAdditions` with `CommitPreparedGenerations`. Protection APIs are reference-count based and can leak obsolete readers if not balanced. Fallback reads must only be used when the file is not manifest-visible.

## Test Signals
Header-level test signals come from consumers: flush generation tests should verify FIFO behavior, rollback tests should verify initial-garbage accounting, read tests should verify footerless direct-write fallback, and cache tests should verify eviction when mappings/protection are removed.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_partition_manager.h -->
