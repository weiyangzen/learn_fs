# sources/storage-engines/rocksdb/table/block_based/block_based_table_builder.cc

## Purpose

`block_based_table_builder.cc` implements `BlockBasedTableBuilder`, the writer for RocksDB block-based SST files. It accepts sorted internal keys, builds data blocks, range-deletion blocks, filters, index blocks, properties, optional compression dictionary blocks, the metaindex, and the footer. It also handles compression selection and verification, optional dictionary sampling, block-cache prepopulation, parallel data-block compression/writing, per-file table properties, alignment padding, and checksum trailers.

## Important APIs, types, and functions

- `CreateFilterBlockBuilder` chooses a full or partitioned filter builder based on table options, filter policy, partition settings, timestamp persistence, and index-builder coupling.
- `BlockBasedTableBuilder::Rep` owns nearly all mutable builder state: options, file writer, offset, block builders, filter/index builders, compression objects, table properties, status, cache keys, parallel compression state, dictionary buffers, and tail-size accounting.
- `BlockBasedTableBuilder::BlockBasedTablePropertiesCollector` writes block-based-table-specific properties such as index type, whole-key filtering, prefix filtering, and decoupled partitioned filters.
- `ParallelCompressionRep` is a lock-free-ish ring-buffer state machine for data-block compression and writing. It tracks emit/compress/write cursors, idle threads, abort/end flags, in-flight size estimates, worker threads, semaphores, and debug watchdog state.
- `Add` validates input value size and key ordering, classifies value types, updates table properties, flushes data blocks when the flush policy says so, feeds filters and index builders, and records range tombstones separately.
- `Flush` finalizes the current data block, optionally samples compression ratios, notifies table property collectors, buffers blocks for dictionary training or emits them for compression and writing, and finalizes filter-block state per data block.
- `MaybeEnterUnbuffered` transitions from dictionary-sampling buffered mode to normal writing by choosing samples, creating a data-block compressor, configuring dictionary-aware verification, replaying buffered blocks into filter/index builders, and emitting all buffered data blocks.
- `EmitBlock` and `EmitBlockForParallel` hand finalized data blocks to the single-threaded or parallel compression/write path and coordinate index-entry preparation/finalization.
- `CompressAndVerifyBlock`, `WriteBlock`, `WriteMaybeCompressedBlock`, and `WriteMaybeCompressedBlockImpl` compress blocks when allowed, verify compression if configured, append block payloads and trailers, update offsets/properties, optionally pad for alignment, and optionally warm the block cache.
- `WriteFilterBlock`, `WriteIndexBlock`, `WriteCompressionDictBlock`, `WriteRangeDelBlock`, `WritePropertiesBlock`, and `WriteFooter` write the tail of the SST.
- `Finish` drives final flush, buffered-to-unbuffered transition, parallel worker shutdown, tail block writing, metaindex/footer writing, final state closure, and status return.

## Control flow

Construction sanitizes table options, creates `Rep`, sets up the base cache key, starts parallel compression if eligible, and allocates a reusable compressed output buffer for the single-threaded path. `Rep` construction is the main configuration phase: it creates compressors/decompressors, decides whether dictionary sampling requires `kBuffered` state, configures compression sampling, reserves cache budget for dictionary buffers, creates the proper index builder, optionally wraps it with a user-defined index builder, creates the filter builder, installs table property collectors, initializes properties, and validates incompatible options such as block alignment with compression.

`Add` is the hot ingestion path. For regular value types, it checks ordering in debug builds, asks `flush_block_policy` whether the existing data block should be flushed before adding the new key, adds the previous-key-aware filter entry in unbuffered mode, appends the key/value to `data_block`, updates `last_ikey`, notifies the index builder only when unbuffered, and notifies table property collectors. Range deletions go to `range_del_block`, with timestamp stripping applied to the tombstone end key when user timestamps are not persisted.

`Flush` finalizes a data block by calling `data_block.Finish()`. It performs optional compression sampling in the emit thread because table property collectors are not thread-safe and need serialized block accounting. In buffered mode, it swaps the block bytes into `data_block_buffers`, updates buffered byte counts, and calls `MaybeEnterUnbuffered`. In unbuffered mode, it increments `num_data_blocks`, finalizes filter state for the block, and either emits the block into the parallel ring buffer or writes it directly.

Parallel compression splits work into emit, compress, and write roles. The emit thread owns creation of uncompressed block bytes and prepared index entries. Worker threads can compress blocks and one worker at a time writes the next block in file order. `ParallelCompressionRep::StateTransition` uses packed atomic bit fields to assign work, track ready-to-write slots, put threads idle, wake idle threads, and stop or abort. `BGWorker` loops over assigned states and calls compression/write helpers. On error it stores the IO status and sets abort.

`MaybeEnterUnbuffered` handles dictionary training. It waits until finish, buffer limit, or cache reservation pressure forces the transition. It selects samples across buffered blocks using a prime-step traversal, creates the data-block compressor with those samples, configures dictionary-aware decompression verification, re-reads buffered blocks through `Block`/`DataBlockIter`, replays keys into filters and index builders, determines next-block first keys for index separators, emits each buffered block, then clears buffer memory and releases cache reservation.

`Finish` flushes the final data block with no next key, forces dictionary-buffer replay if still buffered, stops parallel compression after all emitted blocks are written, records the tail start offset, writes filter, index, compression dictionary, range deletion, properties, metaindex, and footer blocks, marks the builder closed, records actual tail size, and returns the first stored status.

## State and persistence behavior

The persistent file is written as a sequence of blocks followed by the footer. Each block append consists of block payload, one-byte compression type, and four-byte checksum. The checksum includes the block contents, compression type byte, and a context modifier derived from the per-file base context checksum and block offset for newer format versions. Data blocks may be padded for super-block or block alignment, and index delta encoding can be skipped for the first block after alignment padding.

Data block bytes are persisted before the tail. Tail order is filter, index, compression dictionary, range deletion, properties, metaindex, and footer. Depending on format version, the index handle is either placed in the footer or recorded in the metaindex. Table properties persist compression details, index/filter details, timestamps, sequence-number bounds, compression sampling estimates, compression rejection/bypass counts, data sizes, tail offsets, and user-collected properties.

Builder state transitions are explicit: `kBuffered` accumulates uncompressed data blocks for dictionary sampling, `kUnbuffered` writes blocks as they are finalized, and `kClosed` is required before destruction. Status is stored as `IOStatus` protected by a mutex for the rare error case and an atomic OK flag for hot paths. Parallel compression adds in-flight block state in `pc_rep` and makes `EstimatedFileSize()` include upper-bound in-flight size.

## Dependencies and integration points

The builder integrates with `BlockBuilder`, `IndexBuilder` and partitioned index builders, `FilterBlockBuilder` implementations, user-defined index wrappers, `PropertyBlockBuilder`, `MetaIndexBuilder`, `FooterBuilder`, `WritableFileWriter`, `CompressionManager`/`Compressor`/`Decompressor`, cache warming helpers, table property collectors, internal key/timestamp helpers, `FlushBlockPolicy`, and RocksDB statistics/logging.

Reader integration depends on persisted properties matching encoding choices: data block restart interval, index block restart interval, separated key/value setting, index value delta encoding, index key user-key status, compression manager name/type set, filter block names, compression dictionary meta block, and checksum context. The buffered dictionary replay path directly uses `Block` and `DataBlockIter`, so reader-side parsing must remain compatible with just-written data blocks.

## Risks and edge cases

- Parallel compression is complex. Correctness depends on ordered writes despite out-of-order compression, correct `NeedsWriter` bits, wakeup accounting, abort propagation, and prepared index entries matching the final block handle.
- Dictionary buffering delays index/filter updates until replay. Any mismatch between `BlockBuilder` output and `Block` replay can corrupt indexes or filters for buffered files.
- `Add` passes approximate file offsets to collectors in parallel mode, which comments acknowledge are not exact.
- User-defined index, partitioned filter coupling, and parallel compression have incompatibilities enforced in the constructor. New option combinations need similar validation.
- Compression verification requires a matching decompressor, especially after dictionary training. Failure to clone a dictionary-aware verifier becomes a builder error.
- Alignment padding mutates file offsets and can force index delta encoding to be skipped. Tests need to verify index handles and separators across padding boundaries.
- Status handling is optimized for the OK case and shared across worker threads. Any new thread path must use `SetIOStatus`/`SetStatus` and abort parallel work on failure.
- Tail size estimation is intentionally conservative and asserted as an overestimate only for a subset of compaction configurations.

## Test signals

The file exposes many sync points for constructor cache-key setup, `Add` skipping, `WriteBlock` compressed-data tampering, compression result-type tampering, checksum tampering, super-block alignment, filter/property block metadata, raw compression dictionary observation, and finish-time parallel IO status injection. High-value tests include sorted-add enforcement, oversized value rejection, range tombstone timestamp stripping, dictionary sampling and replay, cache reservation pressure, all supported index/filter combinations, user-defined index option failures, compression verification failure, block/trailer checksum validation, block alignment and super-block alignment, parallel compression abort and normal shutdown, tail-size estimates, empty-table finish, and cache prepopulation.
