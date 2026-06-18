# sources/storage-engines/rocksdb/include/rocksdb/sst_partitioner.h

Purpose: This header defines the pluggable SST partitioner interface used by compaction to split output SST files on application-significant key boundaries, reducing future write amplification when files are promoted or compacted.

Important APIs and types: `PartitionerResult` has `kNotRequired` and `kRequired`. `PartitionerRequest` carries pointers to previous and current user keys plus current output file size. `SstPartitioner` declares `Name()`, `ShouldPartition()`, `CanDoTrivialMove()`, and nested `Context` containing full/manual compaction flags, output level, and smallest/largest compaction keys. `SstPartitionerFactory` extends `Customizable`, provides `Type()`, `CreateFromString()`, `CreatePartitioner(context)`, and `Name()`. `SstPartitionerFixedPrefix` splits on fixed-prefix changes, and `SstPartitionerFixedPrefixFactory` creates those partitioners. `NewSstPartitionerFixedPrefixFactory()` is the public factory helper.

Control flow: For each key during compaction, RocksDB builds a `PartitionerRequest` and asks `ShouldPartition()`. Returning `kRequired` finishes the current SST with the previous key and starts a new SST with the current key. When compaction could trivially move an existing file, RocksDB calls `CanDoTrivialMove()` with the file's smallest/largest user keys; the partitioner can reject trivial movement if it would violate partition boundaries. The factory creates a fresh partitioner per compaction context.

State and persistence behavior: The partitioner affects persisted SST file boundaries and therefore future compaction overlap/write amplification. It does not persist its own state, but the selected factory and partitioning semantics must remain compatible with the workload and key format. Fixed-prefix partitioning stores only `len_` in the factory/partitioner object.

Dependencies and integration points: It depends on `Customizable`, `rocksdb_namespace.h`, and `Slice`. `ColumnFamilyOptions::sst_partitioner_factory` wires it into compaction. Option-string parsing can instantiate factories through `CreateFromString()`.

Risks and edge cases: Partitioners must not throw exceptions. `PartitionerRequest` holds pointers to caller-owned slices, so implementations must not retain them beyond the call. A bad partitioner can generate too many small files, harm compaction, or reject beneficial trivial moves. Fixed-prefix logic must handle keys shorter than the configured prefix. Since the feature is experimental in `options.h`, compatibility can change.

Test signals: Tests should cover split decisions on prefix changes, no split within a prefix, short-key behavior, current-output-file-size awareness in custom partitioners, `CanDoTrivialMove()` acceptance/rejection, factory creation from string, per-compaction context propagation, and resulting SST boundary/file-count effects after compaction.
