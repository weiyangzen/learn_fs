# sources/storage-engines/rocksdb/table/block_based/block_based_table_builder.h

## Purpose

`block_based_table_builder.h` declares the `BlockBasedTableBuilder` class, RocksDB's `TableBuilder` implementation for block-based SST files. The header defines the public lifecycle and metric surface used by flush, compaction, and external SST writers, and it declares the private helpers that implement block emission, compression, cache insertion, metadata writing, and parallel compression in the `.cc` file.

## Important APIs, types, and functions

- `BlockBasedTableBuilder(const BlockBasedTableOptions&, const TableBuilderOptions&, WritableFileWriter*)` creates a builder writing to a caller-owned file writer.
- `Add(const Slice& key, const Slice& value)` adds sorted internal keys or range deletion records to the table.
- `Finish()` finalizes all data and metadata blocks and stops using the file. `Abandon()` closes the builder without completing the SST.
- `status()` and `io_status()` expose build and I/O failures. Internally the implementation stores errors in `Rep`.
- `NumEntries`, `IsEmpty`, `PreCompressionSize`, `FileSize`, `EstimatedFileSize`, `EstimatedTailSize`, `GetTailSize`, `NeedCompact`, `GetTableProperties`, `GetFileChecksum`, `GetFileChecksumFuncName`, `SetSeqnoTimeTableProperties`, and `GetWorkerCPUMicros` expose builder progress, properties, and diagnostics.
- Private write helpers include `Flush`, `MaybeEnterUnbuffered`, `EmitBlock`, `EmitBlockForParallel`, `WriteBlock`, `WriteMaybeCompressedBlock`, `WriteMaybeCompressedBlockImpl`, and metadata writers for filter, index, properties, compression dictionary, range deletion, and footer blocks.
- Cache and compression helpers include `SetupCacheKeyPrefix`, `InsertBlockInCache`, `InsertBlockInCacheHelper`, `InsertBlockInCompressedCache`, `CompressAndVerifyBlock`, `MaybeStartParallelCompression`, `StopParallelCompression`, and `BGWorker`.
- Forward declarations for `Rep`, `WorkingAreaPair`, and `ParallelCompressionRep` keep implementation-heavy state out of the header.

## Control flow and contracts

The public contract is a standard builder lifecycle: construct, call `Add` zero or more times with sorted keys, then call either `Finish` or `Abandon` before destruction. `Add` must not be called after closure. The destructor asserts the builder is closed, so callers must explicitly finish or abandon.

Flush control is private but important to the class contract. `Flush(const Slice* first_key_in_next_block)` can force a block boundary and is used internally when the flush policy or finish path requires it. The optional next-block first key lets the index builder choose shortened separators for the current data block.

The header separates single-threaded and parallel block emission. `EmitBlock` compresses/writes the block in the caller thread and immediately adds the index entry. `EmitBlockForParallel` hands uncompressed block bytes to the parallel compression framework while preparing enough index state for later finalization by writer workers.

`WriteBlock` is for compressible data/index blocks, while `WriteMaybeCompressedBlock` writes an already chosen compressed or uncompressed payload and block trailer. `WriteMaybeCompressedBlockImpl` returns `IOStatus` and is usable from worker threads.

## State and persistence behavior

Most state is hidden in `Rep`, but the header reveals the persistent responsibilities: data blocks, filter blocks, index blocks, properties block, compression dictionary block, range-deletion block, metaindex block, and footer. `kBlockBasedTableMagicNumber` is exported for the file footer. `kCompressionSizeLimit` prevents attempting compression on blocks larger than the underlying compression libraries can handle.

The builder reports both actual file offset and estimates. `FileSize()` is the current written size, while `EstimatedFileSize()` may include in-flight data when parallel compression is enabled. `EstimatedTailSize()` and `GetTailSize()` distinguish predicted and final post-data-block tail bytes. `PreCompressionSize()` accumulates uncompressed payload plus trailers/padding for compaction statistics.

## Dependencies and integration points

The class implements `TableBuilder` and is constructed by the block-based table factory. It integrates with `WritableFileWriter`, table and column-family options, compression utilities, `BlockBuilder`, `BlockHandle`, `MetaIndexBuilder`, table properties collectors, block cache, flush block policy, listener/file-creation metadata, and sequence-number-to-time properties.

The public APIs are consumed by flush/compaction jobs, ingestion/external-SST writers, and tests. The private APIs are coupled to the `.cc` implementation's `Rep` layout and to reader expectations for block handles, block trailers, metaindex names, footer format, and table properties.

## Risks and edge cases

- The lifecycle precondition is strict: destroying without `Finish` or `Abandon` is a debug assertion failure.
- `Add` ordering is a caller responsibility except for debug checks. A release build that receives unsorted internal keys could write a malformed table.
- Private helpers assume `rep_->state` is appropriate. For example, compression/write helpers assert unbuffered state, and parallel helpers assert a live `ParallelCompressionRep`.
- `skip_delta_encoding` is a subtle cross-layer signal from block alignment to index entry encoding. Callers must pass it for data blocks and preserve it into index building.
- `GetWorkerCPUMicros` only has meaning when parallel compression workers are used.
- The header declares cache insertion helpers for both parsed and compressed cache paths; implementation choices must remain aligned with cache item helpers and table options.

## Test signals

The header exposes `TEST_InjectIOError` in debug builds, which allows tests to force builder failure. Lifecycle tests should cover finish, abandon, status propagation, empty files, range-deletion-only files, file-size estimates, tail-size estimates, worker CPU accounting, and injected I/O errors. Integration tests should verify that all private metadata writers produce blocks discoverable by block-based table readers.
