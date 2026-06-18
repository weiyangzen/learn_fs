# sources/storage-engines/rocksdb/db/range_del_aggregator.cc

## Purpose

`range_del_aggregator.cc` implements RocksDB's in-memory aggregation layer for fragmented range deletion tombstones. It answers point-key visibility questions during reads and compactions, truncates per-file tombstone iterators to SST file bounds, splits tombstone visibility by snapshots, and creates a merged tombstone iterator for compaction output.

## Important APIs, Types, and Functions

The central implemented types are `TruncatedRangeDelIterator`, `ForwardRangeDelIterator`, `ReverseRangeDelIterator`, `RangeDelAggregator::StripeRep`, `ReadRangeDelAggregator`, `CompactionRangeDelAggregator`, and the file-local `TruncatedRangeDelMergingIter`. Important methods include `Seek`, `SeekInternalKey`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `SplitBySnapshot`, direction-specific `ShouldDelete`, `IsRangeOverlapped`, `AddTombstones`, `CompactionRangeDelAggregator::NewIterator`, and `TruncatedRangeDelMergingIter::key/value/Next/SeekToFirst`.

## Control Flow and State Behavior

`TruncatedRangeDelIterator` wraps a `FragmentedRangeTombstoneIterator` and clips its apparent start/end keys to optional SST smallest/largest internal keys. The constructor parses boundaries and adjusts the largest bound carefully: artificial range-deletion extensions are preserved, sequence-zero largest keys are left alone, and straddling user keys have the end sequence decremented so the truncated tombstone covers the file but not the next SST.

Forward and reverse aggregators maintain active and inactive heaps. Forward scans activate iterators whose starts are at or before the lookup key and retire fragments whose ends are before the key. Reverse scans mirror that with start/end ordering reversed. Active iterators are also kept in a sequence-ordered multiset, so `ShouldDelete` is determined by whether the highest visible covering tombstone sequence is newer than the queried internal key sequence.

`StripeRep` owns truncated iterators for a sequence-number stripe and invalidates the opposite traversal cache whenever the caller switches between forward and backward mode. `ReadRangeDelAggregator` has one stripe from `0` through the read upper bound. `CompactionRangeDelAggregator` splits added iterators by snapshot stripes and optionally applies timestamp upper bounds for `full_history_ts_low` and `trim_ts` during deletion decisions.

`NewIterator()` reuses the original parent iterators, merges them by start key with `TruncatedRangeDelMergingIter`, and feeds the stream back through `FragmentedRangeTombstoneList` for compaction persistence.

## Persistence, Dependencies, and Integration

This file does not write durable state itself, but it decides which point keys are hidden by durable range tombstones and which tombstone fragments are emitted into compaction output. It depends on `dbformat`, `range_tombstone_fragmenter`, `InternalIterator`, `TableBuilder`-adjacent types, `BinaryHeap`, and comparator timestamp semantics. It integrates with DB reads, iterator traversal, file-boundary metadata, snapshot-aware compaction, and range tombstone output building.

## Risks and Test Signals

Risks concentrate around internal-key boundary comparisons, user-defined timestamp bounds, traversal-direction cache invalidation, and snapshot stripe selection. Off-by-one sequence handling at SST boundaries can either leak deleted keys or delete keys from neighboring files. Tests in `range_del_aggregator_test.cc` cover truncation, forward/reverse deletion checks, overlap checks, snapshots, and bounded compaction iterators; fragmenter tests also indirectly protect the expected input shape.
