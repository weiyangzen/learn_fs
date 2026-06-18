# sources/storage-engines/rocksdb/db/range_del_aggregator_test.cc

## Purpose

`range_del_aggregator_test.cc` is the focused GoogleTest suite for the range deletion aggregator. It validates truncated iterator navigation, read-path deletion decisions, range-overlap checks, compaction snapshot semantics, and bounded compaction tombstone output.

## Important APIs, Types, and Helpers

The fixture is `RangeDelAggregatorTest`. Helpers include `MakeRangeDelIter`, `MakeFragmentedTombstoneLists`, `UncutEndpoint`, `InternalValue`, `VerifyIterator`, `VerifySeek`, `VerifySeekForPrev`, `VerifyShouldDelete`, `VerifyIsRangeOverlapped`, `CheckIterPosition`, and `VerifyFragmentedRangeDels`. Local structs describe scan expectations, seek expectations, point deletion cases, and overlap cases.

## Control Flow and State Behavior

The early tests build `FragmentedRangeTombstoneList` objects and wrap them in `TruncatedRangeDelIterator`. `EmptyTruncatedIter`, `UntruncatedIter`, and `UntruncatedIterWithSnapshot` exercise forward/reverse iteration and user-key seeking with and without snapshot upper bounds. `TruncatedIterPartiallyCutTombstones` and `TruncatedIterFullyCutTombstones` verify that SST smallest/largest internal keys clip visible tombstone endpoints exactly.

Read aggregator tests add one or more fragmented iterators to `ReadRangeDelAggregator` and call `ShouldDelete` in forward order and reverse order. They verify deletion depends on both key coverage and tombstone sequence being newer than the queried internal key. Multiple truncated iterator tests simulate adjacent SST file bounds and same-level incremental additions. `IsRangeOverlapped` cases cover empty before/after ranges, boundary-touching ranges, and actual overlaps.

Compaction tests create `CompactionRangeDelAggregator` with no snapshots or snapshots `{9, 19}`. They verify `ShouldDelete` per snapshot stripe and inspect `NewIterator()` output to ensure fragments needed by snapshots are preserved. Bounded iterator tests pass lower/upper internal key slices and confirm empty, clipped, and extra-fragment behavior.

## Persistence, Dependencies, and Integration

The tests are in-memory but model persistent table metadata: serialized range tombstone internal keys, SST file bounds, snapshot stripes, and compaction output fragments. Dependencies include the DB test utilities, `range_tombstone_fragmenter`, `VectorIterator`, and bytewise internal-key comparator.

## Risks and Test Signals

The strongest signals are exact expected tombstone endpoints and sequence numbers after truncation and compaction fragmentation. The suite protects against forward/backward cache divergence, snapshot-stripe deletion mistakes, and bounded compaction output regressions. It does not cover timestamped range tombstones, non-bytewise comparators, or full DB read/compaction integration.
