# sources/storage-engines/rocksdb/table/block_based/block_based_table_reader_sync_and_async.h

## Purpose
Defines the sync and coroutine variants of `BlockBasedTable::RetrieveMultipleBlocks` and `BlockBasedTable::MultiGet`. The file is included twice from `block_based_table_reader.cc` under different coroutine macros, allowing one implementation body to generate blocking and async-capable versions of batched point-read logic.

## Important APIs, Types, And Functions
`RetrieveMultipleBlocks` performs batched data-block reads for `MultiGet`, using `Env::MultiRead` or coroutine `MultiReadAsync`, optional shared scratch memory, direct-I/O buffers, filesystem-provided scratch buffers, checksum verification, corruption reconstruction retry, and cache insertion through `CreateAndPinBlockInCache`.

`MultiGet` implements table-level batched lookup. It applies full or prefix filters to a `MultiGetRange`, seeks the index for each surviving key, groups repeated block handles, issues async block cache lookups, batches disk reads for misses, initializes data block iterators, calls each key's `GetContext::SaveValue`, manages pinned value cleanup when multiple keys reuse the same block, records filter and cache metrics, and writes block cache trace records when enabled.

## Control Flow
`RetrieveMultipleBlocks` first handles mmap reads by falling back to individual `RetrieveBlock` calls. For non-mmap reads, it builds `FSReadRequest` entries from non-null block handles. Adjacent blocks can be combined into one read when using shared scratch or filesystem scratch and not using direct I/O. Requests either point into caller scratch, allocate per-request heap scratch, leave scratch null for direct I/O or filesystem buffers, or later use an `AlignedBuffer` allocation context. The sync path calls `file->MultiRead`; the coroutine path awaits `batch->context()->reader().MultiReadAsync` when not using direct I/O.

After I/O, each request is validated for truncation, wrapped into `BlockContents`, optionally checksum-verified, and retried with `verify_and_reconstruct_read` when checksum corruption is detected and the filesystem supports reconstruction. Good blocks are parsed and inserted or pinned through `CreateAndPinBlockInCache`. Filesystem scratch buffers are explicitly reset after combined reads.

`MultiGet` begins by rejecting empty batches, applying filters, and building an index iterator with hash-prefix compatibility checks. It then scans the filtered range, seeking the index for each key, rejecting keys that fall before a block's `first_internal_key`, lazily loading the uncompression dictionary, marking repeated block offsets with null handles, and starting async block cache lookups for unique handles. Cache hits populate result entries; misses contribute to the cumulative read length. Misses are read with `RetrieveMultipleBlocks`, using stack scratch for small compressed batches, heap scratch for larger ones, filesystem scratch when supported, or direct-I/O handling as required.

Finally, `MultiGet` walks the surviving keys, reuses loaded blocks where possible, creates `DataBlockIter` instances, honors cache-only `Status::Incomplete` by marking keys as may-exist, saves values through `GetContext`, handles merge/value pinning cleanup sharing for reused blocks, scans following blocks when needed, updates filter true-positive counters, and stores per-key statuses.

## State And Persistence Behavior
The file does not alter SST persistence. It mutates per-call `MultiGetRange` state by skipping filtered or resolved keys and writing each key's status. It fills temporary arrays of block handles, statuses, `CachableEntry<Block_kData>`, async cache handles, cache keys, and lookup contexts. It can insert blocks into block cache, increment per-read `GetContext` stats, record perf counters, and write block cache trace records.

Pinned value state is managed through `SharedCleanablePtr` when adjacent keys reuse a block. This avoids extra block cache references while ensuring a cached block is released only after all returned pinned values are done. Scratch buffers are stack, heap, direct-I/O, or filesystem-owned depending on block compression, file mode, and filesystem features.

## Dependencies And Integration Points
The implementation depends on coroutine macros from `util/coro_utils.h`, `AlignedBuffer`, `AsyncFileReader`, `RandomAccessFileReader::MultiRead`, `MultiGetContext`, `BlockCacheInterface`, `BlockCreateContext`, `UncompressionDictReader`, `CreateAndPinBlockInCache`, `NewDataBlockIterator`, filter readers, index iterators, checksum utilities, filesystem feature detection, `GetContext`, and block cache tracing.

It is compiled into both regular and async table reader methods. DB batched point reads, async I/O experiments, tiered/secondary cache paths, direct I/O reads, and block cache tracing all depend on this code staying behaviorally aligned between sync and coroutine expansion.

## Risks And Edge Cases
Batch ordering and index-to-result mapping are fragile because null handles represent both skipped reused blocks and already cached blocks. `reused_mask`, `idx_in_batch`, cache lookup indexes, request indexes, and skipped `MultiGetRange` entries must stay aligned. Combined reads must compute offsets correctly or checksum and block parsing will read the wrong bytes. Direct I/O, filesystem scratch, heap scratch, and compressed-block paths each have different ownership rules.

Cache-only reads must return may-exist rather than false negatives. User-defined timestamps prevent early stop on some hash-seek misses. `first_internal_key` boundary checks must avoid scanning blocks that cannot contain the key. Shared cleanup for reused pinned blocks must not double-release or miss a release. The comment notes some break paths can bypass data-block trace record writing, which is a diagnostic completeness risk.

## Test Signals
`block_based_table_reader_test.cc` contains `BlockBasedTableReaderGetTest`, MultiScan and async MultiScan parameterized tests, first-internal-key boundary tests, prefetch-size and unpin-previous-block tests, and cache-related assertions that exercise much of this machinery. DB-level `MultiGet` tests, tiered secondary cache tests, direct I/O tests, read-scoped block buffer provider stress flags, corruption/checksum tests, and async I/O builds provide additional coverage. A key regression signal is mismatch between sync and coroutine behavior because both are generated from this one header.
