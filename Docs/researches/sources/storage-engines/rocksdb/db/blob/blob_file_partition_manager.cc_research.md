<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_partition_manager.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_file_partition_manager.cc

## Purpose
Implements `BlobFilePartitionManager`, the write-path manager for blob direct write files. It partitions appended blob records across configurable writer slots, tracks blob files across mutable and immutable memtable generations, seals files at flush time, records initial garbage from failed transformed writes, and provides a direct-write read fallback before files become manifest-visible.

## Important APIs, Types, and Functions
The file defines the default `RoundRobinBlobFilePartitionStrategy`, thread-local direct-write compression state, and all manager methods declared in the header. `OpenNewBlobFile` allocates a file number, registers manager ownership, creates a `WritableFileWriter`, writes a `BlobLogHeader`, and initializes partition metadata. `WriteBlob` compresses if needed, chooses a partition, rolls files on column family, compression, or size changes, appends a `BlobLogRecord`, updates offsets and counters, and optionally prepopulates the blob cache. `RotateCurrentGeneration`, `PrepareFlushAdditions`, and `CommitPreparedGenerations` implement the memtable-generation lifecycle. `ResolveBlobDirectWriteIndex` bridges normal `Version::GetBlob` reads and footer-skipping reads of files still owned by direct write.

## Control Flow
Writes compress outside the manager mutex, then enter the selected partition under `mutex_`. If the active file is incompatible or would exceed `blob_file_size_`, it is finalized into `current_generation_sealed_files_`; otherwise the existing writer is reused. On memtable switch, current sealed files and any still-open partition writers move into a FIFO `GenerationBatch`. Flush preparation seals deferred files exactly once, appends their `BlobFileAddition` records and optional `BlobFileGarbage`, and leaves the generation queued until manifest commit calls `CommitPreparedGenerations`.

## State and Persistence Behavior
Persistent state is the physical blob log file plus the manifest edits returned during flush. Open and deferred files remain in `file_to_partition_` so obsolete-file collection knows they are manager-owned. Sealed direct-write files can also be reference-counted in `protected_blob_file_refs_` while live memtables or old SuperVersions may still point at them. Sealing writes a footer, syncs/closes through `BlobLogWriter::AppendFooter`, invokes completion callbacks, and transfers checksum metadata into `BlobFileAddition`. Cache eviction happens when manager-owned mappings are removed or protection drops to zero to avoid keeping footer-less readers after a file is finalized.

## Dependencies and Integration Points
This implementation depends on blob log format/writer/reader/cache components, `Version` blob reads, RocksDB file creation utilities, checksum handoff, event listeners, IO tracing, statistics, compression managers, and DB version metadata. The manager is called from write batching, memtable switch/flush commit paths, blob file cache reads, obsolete-file protection, and direct-write rollback handling.

## Risks and Edge Cases
The generation FIFO must stay exactly aligned with memtable flush ordering; missing or extra generations produce corruption. Failed seal operations remove file mappings and reset partition state, so callers must treat them as hard failures. Compression settings are cached per thread and rebuilt when mutable options change. Direct-write cache prepopulation failures are logged but do not fail the write. `MarkBlobWriteAsGarbage` must be able to find records in active, current sealed, deferred, or pending sealed state; otherwise rollback accounting returns corruption. `ResolveBlobDirectWriteIndex` intentionally propagates manifest-visible failures rather than masking them with fallback reads.

## Test Signals
No tests are in this file, but related coverage is expected through direct-write DB tests and blob reader tests. Observable behaviors include partition selection modulo bounds, file rollover, retry-safe flush preparation, protection reference underflow logging, stale footer-less reader eviction, and corruption retry through uncached reader refresh.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_file_partition_manager.cc -->
