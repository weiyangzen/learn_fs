# sources/storage-engines/rocksdb/db/range_tombstone_fragmenter_test.cc

## Purpose

`range_tombstone_fragmenter_test.cc` is the unit test suite for range tombstone fragmentation and iterator navigation. It specifies how overlapping, contiguous, repeated, unordered, and snapshot-filtered range tombstones are transformed into non-overlapping fragments.

## Important APIs, Types, and Helpers

The fixture is `RangeTombstoneFragmenterTest`. Helpers include `MakeRangeDelIter`, `CheckIterPosition`, `VerifyFragmentedRangeDels`, `VerifyVisibleTombstones`, `VerifySeek`, `VerifySeekForPrev`, and `VerifyMaxCoveringTombstoneSeqnum`. Test structs encode seek and max-covering-sequence expectations.

## Control Flow and State Behavior

Basic tests cover non-overlapping tombstones, overlapping tombstones, contiguous ranges, repeated start/end keys, repeated start keys with different end keys, and mixed repeated starts. Expected output lists show each non-overlapping fragment and each sequence in descending order within that fragment.

The overlap tests create multiple iterators over the same fragmented list with different upper bounds and verify both raw fragment iteration and top-visible iteration. They also verify `MaxCoveringTombstoneSeqnum` at starts, covered interior keys, exact end keys, gaps, and out-of-range positions.

Compaction-specific tests construct `FragmentedRangeTombstoneList` with `for_compaction=true`. Without snapshots, only the newest covering tombstone per fragment is retained. With snapshots, additional sequence numbers needed by snapshot stripes are preserved. `IteratorSplitNoSnapshots` and `IteratorSplitWithSnapshots` validate the map of split iterators and their lower/upper bounds.

Seek tests cover targets equal to start keys, inside covered ranges, equal to end keys, and outside all tombstones for both `Seek` and `SeekForPrev`. The unordered-input test confirms sorting is applied and the unfragmented tombstone counter remains correct.

## Persistence, Dependencies, and Integration

The suite is in-memory, using serialized `RangeTombstone` records through `VectorIterator`, but it reflects the format stored in range-delete meta blocks and consumed by table/memtable readers.

## Risks and Test Signals

The strongest signals are exact fragment streams and top-visible streams across overlapping data. Edge cases around exact end-key exclusivity, repeated starts, snapshot stripe bounds, and unordered input are explicitly covered. Timestamped range tombstone behavior is not covered here.
