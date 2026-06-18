# sources/storage-engines/rocksdb/table/block_based/multi_scan_index_iterator.cc

## Purpose
Implements an index iterator over a precomputed set of data block handles for multi-scan reads. It walks only blocks relevant to prepared scan ranges, releases prefetched blocks as they become unnecessary, and reports prefetch waste and limit conditions.

## Important APIs, Types, And Functions
`MultiScanIndexIterator` implements constructor, destructor, `ReleaseBlocks`, `Seek`, `SeekToBlock`, `SeekToBlockIdx`, `SetExhausted`, `Next`, `SeekToFirst`, reverse-positioning stubs, `key`, `user_key`, `value`, and `GetMaxPrefetchSize`. It uses `MultiScanArgs`, `ReadSet`, `BlockHandle`, data-block separators, per-scan block index ranges, `InternalKeyComparator`, and statistics ticks.

## Control Flow
`Seek` is forward-only and tracks the previous seek key. It maps the seek target to prepared scan ranges: before the next range start, after it, or exactly at it. It then positions to the correct block or marks the current range exhausted. `SeekToBlock` advances `next_scan_idx_`, releases skipped blocks, linearly scans separators to find the first block whose separator is not less than the target, and delegates to `SeekToBlockIdx`. `Next` releases the current block, advances, checks current scan-range end, and stops with `Status::PrefetchLimitReached` if it crosses the prefetch window. `SetExhausted` distinguishes out-of-bound for an exhausted range from natural EOF after the last range.

## State And Persistence Behavior
There is no persistence. Runtime state includes owned vectors of block handles/separators/ranges, borrowed scan options, a shared `ReadSet` for pinned block lifetime, current and next scan indexes, valid/exhausted flags, previous seek key, status, and wasted-prefetch count. The destructor releases any remaining pinned blocks and records `MULTISCAN_PREFETCH_BLOCKS_WASTED`.

## Dependencies And Integration Points
Depends on multi-scan table-reader infrastructure, `ReadSet::ReleaseBlock`, internal key formatting, user comparator timestamp-aware comparisons, `Statistics`, and perf tick definitions. Returned `IndexValue`s feed downstream data-block iteration while disabling first-key optimization by using an empty first internal key.

## Risks And Edge Cases
The iterator is intentionally forward-only; backward operations invalidate it. Seek targets before earlier prepared ranges are invalid and counted as seek errors. Correct block release is delicate because `SeekToBlock` may release blocks before updating `cur_idx_`, and the destructor must avoid double-release. Separator comparisons use user keys without timestamps, so range starts and separators must be in the same comparator domain. Prefetch limit status is used to trigger additional prefetch rather than signal table corruption.

## Test Signals
Expected signals include correct block-handle sequence for multiple scan ranges, `is_out_of_bound_` behavior when a prepared range is exhausted, `PrefetchLimitReached` when crossing a bounded prefetch window, released-block accounting, wasted-prefetch statistics, and invalid reverse iteration.
