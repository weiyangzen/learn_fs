# sources/storage-engines/rocksdb/db/range_tombstone_fragmenter.h

## Purpose

`range_tombstone_fragmenter.h` declares RocksDB's fragmented range tombstone storage and iterator interfaces. These abstractions provide compact non-overlapping stacks of range deletions and visibility-filtered navigation for reads and compactions.

## Important APIs and Types

`FragmentedRangeTombstoneList` owns `RangeTombstoneStack` entries, flattened sequence-number and timestamp vectors, pinned backing storage, source iterator pinning, and counters for unfragmented tombstones and payload bytes. `ContainsRange(lower, upper)` lazily builds a sequence set to test whether any tombstone sequence exists in a stripe.

`FragmentedRangeTombstoneListCache` is a reader cache wrapper with a mutex, unique list pointer, and atomic initialized flag.

`FragmentedRangeTombstoneIterator` derives from `InternalIterator` but documents that `Seek` and `SeekForPrev` are specialized for range tombstone coverage rather than generic internal-key iteration. It supports raw stack iteration (`SeekToFirst`, `Next`, `Prev`) and top-visible iteration (`SeekToTopFirst`, `TopNext`, `TopPrev`). It exposes `Tombstone`, `start_key`, `end_key`, `seq`, `timestamp`, `parsed_start_key`, `parsed_end_key`, `MaxCoveringTombstoneSeqnum`, `SplitBySnapshot`, and sequence bounds.

## Control Flow and State Behavior

The header's data model separates interval positions from sequence/timestamp positions. A `RangeTombstoneStack` represents one non-overlapping key range and indexes into the flattened seq/timestamp arrays. Visibility is calculated by `SetMaxVisibleSeqAndTimestamp()`, which finds the first sequence not above `upper_bound_`, then advances further if a timestamp upper bound requires an older timestamp. Lower-bound filtering is applied by forward/backward visible scans.

The header explicitly warns that `icmp_` may not outlive the iterator after construction. Long-lived navigation must use the stored user comparator `ucmp_`; only construction-time work such as `SplitBySnapshot` may dereference `icmp_`.

## Persistence, Dependencies, and Integration

This interface is used by table readers, memtables, range deletion aggregators, repair table scanning, and compaction output construction. Dependencies include `dbformat`, `PinnedIteratorsManager`, `InternalIterator`, `Status`, sequence-number types, and comparator timestamp APIs.

## Risks and Test Signals

The main risks are lifetime and comparator misuse, timestamp ordering consistency with sequence ordering, and callers assuming generic `InternalIterator` seek semantics. Tests in `range_tombstone_fragmenter_test.cc` validate stack ordering, visibility under sequence bounds, split-by-snapshot bounds, seek edge cases, and unordered input accounting.
