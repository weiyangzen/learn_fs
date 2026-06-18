# sources/storage-engines/rocksdb/table/block_based/block_based_table_iterator.h

## Purpose
`block_based_table_iterator.h` declares `BlockBasedTableIterator`, RocksDB's internal iterator for walking the key/value entries of a `BlockBasedTable`. The declaration exposes the iterator contract used by upper layers and defines the private state machine for block loading, bounds, prefix filtering, pinning, readahead, async IO, lazy value preparation, and MultiScan.

## Important APIs, Types, And Functions
The constructor takes a `BlockBasedTable*`, long-lived `ReadOptions&`, `InternalKeyComparator&`, owned index iterator over `IndexValue`, filter and upper-bound behavior flags, prefix extractor, caller identity, optional compaction readahead size, and `allow_unprepared_value`. It initializes `BlockCacheLookupContext`, `BlockPrefetcher`, table level state, and MultiScan status.

The public iterator API overrides `Seek()`, `SeekForPrev()`, `SeekToFirst()`, `SeekToLast()`, `Next()`, `NextAndGetResult()`, `Prev()`, `Valid()`, `key()`, `user_key()`, `value()`, `status()`, `PrepareValue()`, `write_unix_time()`, `UpperBoundCheckResult()`, pinned-iterator hooks, readahead state get/set hooks, and `Prepare(const MultiScanArgs*)`.

`Valid()` requires not out-of-bound, MultiScan status OK, and either a deferred first-key-from-index position or a valid real data-block iterator. `key()` and `user_key()` switch between index first-key metadata and `DataBlockIter` depending on `is_at_first_key_from_index_`. `PrepareValue()` materializes a deferred block. `value()` records useful-seek statistics and returns the data-block value after materialization.

`write_unix_time()` parses the current internal key, handles unknown-before-all sequence/time sentinels, uses the table's `SeqnoToTimeMapping`, and for `kTypeValuePreferredSeqno` obtains the sequence number from the packed value before mapping it to a proximal write time.

`status()` prioritizes `multi_scan_status_`, then current index status when the index is expected to be at the current block, then data-block status, then async `TryAgain`, otherwise OK. `UpperBoundCheckResult()` exposes whether the iterator is known out of bound, known in bound for the current block, or unknown.

Pinning APIs report whether keys/values are pinned by the index value or block iterator and delegate block iterator cleanups to a `PinnedIteratorsManager` when resetting a real block. `GetReadaheadState()` and `SetReadaheadState()` transfer adaptive readahead state through `ReadaheadFileInfo`.

Private types include `IterDirection`, `BlockUpperBound`, `SeekStatState`, and `BlockHandleInfo`. Private helpers include `ResetMultiScan()`, `SeekSecondPass()`, `SeekImpl()`, `InitDataBlock()`, `AsyncInitDataBlock()`, `MaterializeCurrentBlock()`, block/key discovery functions, bound checks, prefix filter checks, readahead cache lookup helpers, and `CollectBlockHandles()` for MultiScan.

## Control Flow
The header defines a two-layer iteration model. The index iterator locates data blocks and provides `IndexValue` metadata; the data-block iterator walks entries inside a loaded block. Public seek/movement methods coordinate these layers through private helpers and state flags.

Lazy key exposure is part of the public contract: when `is_at_first_key_from_index_` is true, `key()` returns `index_iter_->value().first_internal_key`, and `PrepareValue()` must be called to initialize `block_iter_` before reading `value()`. This supports block cache readahead lookup and reduced data-block reads for callers that only need keys.

Bounds and prefix checks are split. `CheckPrefixMayMatch()` can skip data-block reads when the table filter says a prefix range cannot match, but it returns true for backward iteration when upper-bound checking is required. Upper-bound state is maintained separately through `block_upper_bound_check_` and `is_out_of_bound_`.

Readahead state has explicit reset and queue helpers. `ResetBlockCacheLookupVar()` clears out-of-bound readahead state, disables lookup-ahead, and clears queued block handles. `IsNextBlockOutOfReadaheadBound()` stops readahead at iterate upper bound or prefix boundary. `InitializeStartAndEndOffsets()` and `BlockCacheLookupForReadAheadSize()` are declared for implementation in the `.cc` file.

MultiScan state is declared as an optional replacement for the normal index iterator. `Prepare()` installs a `MultiScanIndexIterator`, while `ResetMultiScan()` releases the `ReadSet`, clears pointers and limits, permits/discards previous MultiScan errors, and restores the saved original index iterator.

## State And Persistence Behavior
The class keeps runtime-only iteration state. It does not persist data; it reads table blocks and reports iterator positions. `read_options_` is a reference that must outlive the iterator, making lifetime management important.

Core position state includes `index_iter_`, `block_iter_`, `prev_block_offset_`, `block_iter_points_to_real_block_`, and `is_index_at_curr_block_`. Correctness depends on knowing when the index iterator and block iterator refer to the same data block.

Adaptive/readahead state includes `block_prefetcher_`, optional `block_handles_`, prefix string `seek_key_prefix_for_readahead_trimming_`, `readahead_cache_lookup_`, `is_index_out_of_bound_`, and `direction_`. `BlockHandleInfo` owns copied first-key bytes so slices remain valid after index iterator movement.

Bound/filter/lazy state includes `allow_unprepared_value_`, `block_upper_bound_check_`, `is_at_first_key_from_index_`, `check_filter_`, `need_upper_bound_check_`, `is_out_of_bound_`, and `seek_stat_state_`. Async state is the boolean `async_read_in_progress_`.

MultiScan state includes a status object, shared `ReadSet`, raw pointer to the active `MultiScanIndexIterator`, saved original index iterator, and `prefetch_max_idx_`. The raw pointer is valid only while the unique pointer stored in `index_iter_` owns the MultiScan iterator.

## Dependencies And Integration Points
The declaration depends on sequence-number-to-time mapping, IO dispatcher types, block-based table reader internals, block prefetching, MultiScan index iteration, and reader common utilities. It uses RocksDB internal iterator, key parsing, comparator, slice transform, prefetch buffer, pinned iterator, statistics, and cache-entry abstractions through included headers.

Upper layers use this class through `InternalIteratorBase<Slice>` for scans, point/range iteration, compaction reads, and MultiScan. Lower layers are accessed through `BlockBasedTable` APIs for filters, data-block iterator creation, cache lookups, table statistics, sequence-to-time mapping, and table representation/options.

## Risks And Edge Cases
Because `index_iter_` is public, tests or nearby code can inspect or manipulate it directly; production correctness still assumes private methods maintain synchronization flags. Any direct mutation outside the class can invalidate assumptions.

The iterator stores several borrowed references and raw pointers: table, read options, comparator, prefix extractor, pinned manager, and MultiScan raw pointer. Lifetime and ownership must follow the table reader and iterator contracts.

`status()` deliberately ignores `index_iter_->NotFound()` for prefix indexes and only checks index status when the index is considered current. Bugs in `is_index_at_curr_block_` could hide or misattribute index errors.

`IsNextBlockOutOfReadaheadBound()` assumes `prefix_extractor_` is usable when `prefix_same_as_start` and a non-empty seek prefix are active. Constructor call sites must keep prefix extractor consistency with read options.

`ResetDataIter()` delegates cleanups when pinning is enabled, invalidates the block iterator, and clears upper-bound knowledge. Missing calls before block switches would risk pinned-resource lifetime bugs or stale bound answers.

MultiScan reset discards MultiScan errors when falling back to regular iteration. That is intentional for backward/fallback paths, but tests should verify real read errors are still visible while MultiScan remains active.

## Test Signals
Declaration-level contracts should be covered by iterator API tests for validity, status ordering, key/user-key sources in deferred versus materialized positions, value preparation, write-time mapping, upper-bound result states, pinning reports, readahead state transfer, and fallback from MultiScan to normal index iteration.

State-machine tests should explicitly exercise transitions among no real block, real block loaded, deferred first-key, async in-progress, index moved ahead by readahead lookup, out-of-bound, and MultiScan active. Tests should also verify cleanup delegation with pinned iterators and that `TEST_IsBlockPinnedByMultiScan()` reflects read-set availability only during active MultiScan.
