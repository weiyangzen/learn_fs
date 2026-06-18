# sources/storage-engines/rocksdb/db/db_iter.cc

## Purpose

`db_iter.cc` implements `DBIter`, the user-facing RocksDB iterator that converts an ordered stream of internal keys into visible user keys at a snapshot/read sequence. It hides overwritten versions, tombstones, invisible sequence numbers, and timestamp-filtered records; resolves merge operands; optionally fetches blob values; materializes wide-column entities; handles forward/reverse scans and direction changes; records iterator statistics; and coordinates newer read-path optimizations such as contiguous point-tombstone conversion into memtable range tombstones.

## Important APIs, types, and functions

`DBIter::DBIter` wires together `ReadOptions`, immutable/mutable CF options, the wrapped `InternalIterator`, optional `Version`, `ReadCallback`, active memtable, DB tracing, blob state, timestamp bounds, prefix behavior, and flush/range-tombstone thresholds. `HasFullTimestampVisibility()` gates read-path range tombstone conversion so it is only enabled when timestamp filtering cannot hide interior live keys.

Navigation is implemented by `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `Next`, `Prev`, `FindNextUserEntryInternal`, `PrevInternal`, `ReverseToForward`, `ReverseToBackward`, `FindValueForCurrentKey`, `FindValueForCurrentKeyUsingSeek`, and `FindUserKeyBeforeSavedKey`.

Value handling is split across `PrepareValueInternal`, `SetValueAndColumnsFromPlain`, `SetValueAndColumnsFromBlob`, `SetValueAndColumnsFromBlobImpl`, `SetValueAndColumnsFromEntity`, `MaterializeLazyEntityColumns`, `PrepareValue`, `MergeValuesNewToOld`, `MergeWithNoBaseValue`, `MergeWithPlainBaseValue`, `MergeWithBlobBaseValue`, `MergeWithWideColumnBaseValue`, and `SetValueAndColumnsFromMergeResult`.

Range and skip accounting is handled by `TrackContiguousTombstone`, `FlushPendingTombstoneRun`, `MaybeInsertRangeTombstone`, `TooManyInternalKeysSkipped`, `IsVisible`, `SetSavedKeyToSeekTarget`, `SetSavedKeyToSeekForPrevTarget`, and the `Prepare`/`ValidateScanOptions`/`SetScanOptionsForPrepare` multi-scan path.

## Control flow

Forward iteration starts with a seek target encoded as an internal key using the read sequence and `kValueTypeForSeek`. `FindNextUserEntryInternal()` loops over internal records until it finds a visible user entry. It skips newer sequence numbers, timestamp-filtered versions, duplicate versions of the saved user key, and records hidden by visible deletions. For values it prepares the underlying iterator value, flushes any pending tombstone run, saves the user key, and populates plain/blob/wide-column state. For merge records it enters `MergeValuesNewToOld()`, accumulating operands from newest to oldest until it reaches a deletion, base value, blob base, wide-column base, or key boundary.

Reverse iteration keeps a different invariant: the internal iterator is positioned before the exposed user key. `Prev()` converts from forward state through `ReverseToBackward()` when needed, then `PrevInternal()` scans lower keys. `FindValueForCurrentKey()` walks versions for the current user key from old-to-new iterator position, keeps only visible versions, requires pinned values for reverse presentation, tracks deletion vs value vs merge base type, and may switch to `FindValueForCurrentKeyUsingSeek()` when too many versions make linear reverse scanning expensive.

Direction changes are explicit. `ReverseToForward()` seeks or advances until the internal iterator is at or after the current saved key. `ReverseToBackward()` seeks around a merged current entry if necessary and then calls `FindUserKeyBeforeSavedKey()` to restore the reverse invariant.

Seek methods reset temporary pinned data, blob state, value/column state, skipped-key counters, tombstone tracking, and prefix state. They record trace events, enforce lower/upper bounds, optionally extract a prefix for prefix-same-as-start or tombstone conversion, then delegate to the forward or reverse finder.

## State and persistence behavior

Most state is per-iterator and transient: `saved_key_`, `ikey_`, `saved_write_unix_time_`, merge operands, pinned iterator manager, value/blob state, timestamp bounds, scan range index, direction, and validity. Statistics are buffered in `LocalStatistics` in the header and flushed to global tickers in the destructor.

There is one important read-path mutation: when configured and safe, contiguous visible point tombstones observed during reads can be inserted into the active memtable as logically redundant range tombstones. `MaybeInsertRangeTombstone()` refuses insertion if the run is below threshold, no active memtable exists, the iterator snapshot predates the memtable, prepared/uncommitted writes could be shadowed, or an existing range tombstone already covers the span. It inserts at the read sequence under the CF ingest-SST lock and records inserted/discarded tickers.

The iterator can also mark the active memtable for flush when too many hidden active-memtable operations are scanned, either per operation or averaged since the last seek. This is another read-side feedback path into storage state.

## Dependencies and integration points

`DBIter` integrates with `InternalIterator`, `IteratorWrapper`, `Version::GetBlob`, `BlobFilePartitionManager`, `BlobFetcher`, `WideColumnSerialization`, `ReadPathBlobResolver`, `MergeHelper`, `MergeContext`, `ReadCallback`, `ReadOnlyMemTable`, `ColumnFamilyData`, `DBImpl` tracing, `IODispatcher`, `PinnedIteratorsManager`, `ThreadStatusUtil`, `PerfContext`, `Statistics`, user comparators with timestamp support, and range tombstone iterators.

External callers reach this implementation through `DBIter::NewIter` declared in `db_iter.h`, normally via DB read APIs constructing iterators over memtables and SSTs.

## Risks and edge cases

Correctness depends on strict internal-iterator ordering by user key, sequence, and value type. The code has many direction-specific invariants, especially around merged entries and reverse iteration requiring pinned values. Timestamp range mode changes key skipping and can expose multiple versions of a user key, so comparisons switch between timestamp-aware and timestamp-stripped forms. Lazy blob and entity paths must preserve backing storage when the underlying iterator moves; the implementation copies serialized entities before lazy deserialization to avoid dangling slices and self-aliased string assignment.

Range tombstone conversion is deliberately conservative because a table filter, prefix bloom behavior, timestamp filtering, old snapshots, or uncommitted writes can make a read-observed deletion run unsafe to convert. `max_skippable_internal_keys` can terminate scans with `Incomplete`, so callers must treat status as part of iterator validity. Multi-scan preparation requires exact seek order and matching upper bounds; misuse returns `InvalidArgument`.

## Test signals

This implementation is directly stressed by `db_iter_stress_test.cc`, which compares random DBIter operations against a reference iterator under injected internal-iterator errors and mutations. Broader RocksDB iterator tests cover timestamps, bounds, merges, blobs, wide columns, prefix scans, and pinning. The implementation itself records many perf and ticker signals: DB seek/next/prev counts, bytes read, internal skips, merge counts, reseeks, read-path range tombstone insert/discard counts, and corruption/incomplete statuses.
