# sources/storage-engines/rocksdb/table/block_based/multi_scan_index_iterator.h

Purpose: declares `MultiScanIndexIterator`, an `InternalIteratorBase<IndexValue>` adapter over a prepared vector of data block handles and per-scan block ranges. Its role is to let `BlockBasedTableIterator` reuse ordinary index-iterator seek and block-finding logic for MultiScan requests rather than adding a separate scan-specific data block path.

Important APIs/types/functions: the constructor takes moved `BlockHandle` and separator vectors, `block_index_ranges_per_scan`, a borrowed `MultiScanArgs`, shared `ReadSet`, prefetch limit, `InternalKeyComparator`, and optional `Statistics`. Public iterator operations include forward-only `Seek`, `Next`, `SeekToFirst`, `Valid`, `key`, `user_key`, `value`, `status`, `current_read_set_index`, `GetMaxPrefetchSize`, `IsScanRangeExhausted`, and `HasMoreScanRanges`. Reverse methods are declared unsupported and invalidate the iterator. Private helpers release skipped prefetched blocks, locate a block for unexpected seek targets, position by index, and mark scan ranges exhausted.

Control flow: callers prepare block metadata elsewhere, then this iterator walks only within the current scan range. `Next` advances block indexes and jumps to the next scan range at range end. `Seek` must be monotonic by `prev_seek_key_`; non-monotonic behavior would violate the forward-only contract and can produce incorrect release/prefetch accounting.

State and persistence: no durable state is written. Runtime state tracks current block index, next scan index, validity, previous seek key, wasted prefetched blocks, and a mutable internal-key buffer synthesized from the current separator plus max sequence number. `ReadSet` is shared and likely owns per-block read/prefetch lifecycle state.

Dependencies/integration: depends on RocksDB internal key encoding, `ReadSet`, `MultiScanArgs`, `InternalKeyComparator`, and table iterator code expecting `IndexValue`. The value intentionally carries an empty first internal key, disabling the first-key-from-index optimization.

Risks and test signals: risk is concentrated in monotonic seek enforcement, releasing skipped blocks exactly once, scan boundary reporting, and lifetime assumptions for borrowed `scan_opts`/`icomp`. This header has no direct tests in the subset; coverage likely comes from MultiScan table iterator tests outside this item.
