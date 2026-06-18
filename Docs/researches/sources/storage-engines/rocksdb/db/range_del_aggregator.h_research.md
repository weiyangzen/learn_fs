# sources/storage-engines/rocksdb/db/range_del_aggregator.h

## Purpose

`range_del_aggregator.h` declares the range deletion aggregation API used by RocksDB readers and compactions. It defines how fragmented range tombstone iterators are clipped to file boundaries, cached for directional scans, split across snapshot stripes, queried for point-key deletion, and re-exposed as a compaction output iterator.

## Important APIs and Types

`TruncatedRangeDelIterator` is a boundary-aware wrapper around `FragmentedRangeTombstoneIterator`. Its API exposes top-fragment navigation, internal-key and user-key seek methods, `start_key`, `end_key`, `seq`, timestamp access, `SplitBySnapshot`, and upper/lower sequence bounds.

`ForwardRangeDelIterator` and `ReverseRangeDelIterator` are traversal caches. They keep inactive iterators ordered by start/end key and active iterators ordered both by range endpoint and maximum sequence number. `SeqMaxComparator` and `StartKeyMinComparator` supply heap/set ordering.

`RangeDelAggregator` is the abstract base with `AddTombstones`, `ShouldDelete`, `InvalidateRangeDelMapPositions`, `IsEmpty`, and `AddFile`. Its nested `StripeRep` owns the actual iterator set for one sequence interval and supports `ShouldDelete` plus `IsRangeOverlapped`.

`ReadRangeDelAggregator` is the read-path implementation with one stripe. `CompactionRangeDelAggregator` adds snapshot striping, `full_history_ts_low`/`trim_ts` filtering for deletion decisions, and `NewIterator()` for persisted compaction tombstones.

## Control Flow and State Behavior

The header encodes an important split between read-time and compaction-time behavior. Reads need a single visible snapshot upper bound, so `ReadRangeDelAggregator` can query one `StripeRep`. Compaction must preserve snapshot-visible history, so `CompactionRangeDelAggregator` maps snapshot upper bounds to `StripeRep` instances and chooses the first stripe whose upper bound is at least the queried sequence.

Directional traversal is explicit through `RangeDelPositioningMode`. Callers that scan forward or backward can reuse heap state, while random seeks or direction changes must invalidate cached positions. This is why the public base exposes `InvalidateRangeDelMapPositions`.

The `files_seen_` set in the base class tracks table file numbers already added to avoid duplicated range tombstone processing by integration code.

## Persistence, Dependencies, and Integration

The declared APIs bridge `FragmentedRangeTombstoneIterator` from table/memtable range-delete metadata to read iterators, compaction iterators, and table-building logic. Dependencies include `dbformat`, `range_tombstone_fragmenter`, `InternalIterator`, `BinaryHeap`, `TableBuilder`, `VersionEdit`, and comparator/timestamp APIs.

## Risks and Test Signals

The header's contracts are tight: `Seek` targets are user keys with timestamps when enabled, while `SeekInternalKey` accepts internal keys. `SplitBySnapshot` children are lifetime-dependent on the parent tombstone list. Timestamp upper bounds affect deletion decisions but should not accidentally filter persisted tombstone output. Tests assert expected behavior through the concrete implementation in `range_del_aggregator_test.cc`.
