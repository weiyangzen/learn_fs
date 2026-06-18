# sources/storage-engines/rocksdb/db/range_tombstone_fragmenter.cc

## Purpose

`range_tombstone_fragmenter.cc` implements conversion from serialized range deletion records into non-overlapping tombstone fragments. It also implements iterators that expose either every fragment sequence or only the top visible tombstone for a sequence/timestamp visibility window.

## Important APIs, Types, and Functions

Implemented APIs include `FragmentedRangeTombstoneList` construction, `FragmentTombstones`, `ContainsRange`, `FragmentedRangeTombstoneIterator` constructors, `SeekToFirst`, `SeekToTopFirst`, `SeekToLast`, `SeekToTopLast`, `Seek`, `SeekForPrev`, `TopNext`, `TopPrev`, `MaxCoveringTombstoneSeqnum`, and `SplitBySnapshot`.

## Control Flow and State Behavior

The list constructor first scans input to count tombstones, measure payload bytes, and detect whether input is sorted by internal start key. If unsorted, or if timestamped tombstone end keys need minimum timestamp padding, it copies keys/values into a `VectorIterator` so fragmentation sees ordered input.

`FragmentTombstones` keeps a working set of currently open tombstones in `cur_end_keys`, ordered by parsed end key. When the start key changes, `flush_current_tombstones` emits one or more non-overlapping `[cur_start_key, cur_end_key)` fragments. For each fragment it gathers covering tombstone sequence numbers, sorts them descending, and optionally sorts timestamps descending. For compaction without user-defined timestamps, only the top sequence visible in each snapshot stripe is preserved; for reads, and for timestamp-enabled compaction, all relevant entries are preserved.

The iterator stores a position into `tombstones_` and a sequence-position into the flattened sequence vector. `SeekToTopFirst`, `SeekToTopLast`, `Seek`, and `SeekForPrev` call `SetMaxVisibleSeqAndTimestamp()` and then scan to the next fragment with a sequence in `[lower_bound_, upper_bound_]` and, when configured, timestamp at or below the timestamp upper bound.

## Persistence, Dependencies, and Integration

The list pins copied slices and the source iterator through `PinnedIteratorsManager`, so fragment slices remain valid. It exposes metadata counts used by table property/reporting paths. It integrates with table range-delete meta blocks, memtable range tombstone iterators, read aggregation, compaction aggregation, and `BuildTable` range tombstone output.

## Risks and Test Signals

Risks include sorted-input detection, timestamp padding, lifetime of pinned slices, empty tombstones, repeated starts/ends, and snapshot compaction dropping too much history. `FragmentedRangeTombstoneIterator` intentionally does not implement normal `InternalIterator` seek semantics, so callers must use it only in expected range-tombstone contexts. `range_tombstone_fragmenter_test.cc` covers overlap fragmentation, unordered input, visible top tombstones, snapshot splitting, seek behavior, and count accounting.
