# sources/storage-engines/rocksdb/db/db_iter_test.cc

## Purpose
`db_iter_test.cc` is a focused RocksDB unit test suite for the user-facing `Iterator` produced by `DBIter::NewIter`. It verifies how DB iteration projects a stream of internal keys into visible user keys under sequence-number snapshots, deletions, single deletions, merge operands, timed puts, forward/reverse direction changes, iterator bounds, prefix scans, and internal skip limits.

The file is not production code, but it is a behavioral specification for `DBIter` and the iterator stack beneath it. It uses synthetic in-memory `InternalIterator` implementations to make precise internal-key layouts, then asserts the visible keys, values, statuses, counters, and movement costs seen by the public iterator API.

## Important APIs, Types, and Functions
The main helper is `TestIterator : public InternalIterator`. It stores `(internal_key, value)` pairs in a vector, sorts them with `InternalKeyComparator`, and implements `SeekToFirst`, `SeekToLast`, `Seek`, `SeekForPrev`, `Next`, `Prev`, `key`, `value`, and `status`. It exposes convenience writers for `AddPut`, `AddTimedPut`, `AddDeletion`, `AddSingleDeletion`, `AddMerge`, and raw `Add`, plus `Finish()` to sort before use. `Vanish()` can remove a user key while iteration is in progress, simulating a forward iterator or memtable view changing after compaction/filtering.

`DBIteratorTest` is the primary GoogleTest fixture. Most test cases construct `Options`, `ImmutableOptions`, `MutableCFOptions`, `ReadOptions`, a `TestIterator`, and then create a public iterator with `DBIter::NewIter(env_, ro, ..., BytewiseComparator(), internal_iter, nullptr /* version */, sequence, nullptr /* read_callback */, nullptr /* active_mem */)`.

Important RocksDB types and APIs exercised include:

- `DBIter::NewIter`, the wrapper that converts internal RocksDB records into public `rocksdb::Iterator` behavior.
- `InternalIterator`, `InternalKeyComparator`, `ParsedInternalKey`, `AppendInternalKey`, `ParseInternalKey`, and `ValueType` variants such as `kTypeValue`, `kTypeValuePreferredSeqno`, `kTypeDeletion`, `kTypeSingleDeletion`, and `kTypeMerge`.
- `ReadOptions` fields `iterate_upper_bound`, `iterate_lower_bound`, `prefix_same_as_start`, and `max_skippable_internal_keys`.
- `Options` fields `merge_operator`, `statistics`, `max_sequential_skip_in_iterations`, and `prefix_extractor`.
- `MergeOperators::CreateFromStringId("stringappend")`, used to make merge results observable as comma-joined strings.
- `PackValueAndWriteTime`, used by timed-put tests to verify `kTypeValuePreferredSeqno` values are unpacked and merged correctly.
- `MultiScanArgs` and `Iterator::Prepare`, used to validate scan-range preflight forwarding.
- `PerfContext` counters such as `internal_key_skipped_count` and `internal_delete_skipped_count`, plus the `NUMBER_OF_RESEEKS_IN_ITERATION` ticker.
- `NewMergingIterator`, `IteratorWrapper`, and `SyncPoint`, used by `DBIterWithMergeIterTest` to stress `DBIter` over a merged set of child iterators while child data changes.

## Control Flow
The tests generally build an ordered internal stream, wrap it in `DBIter`, position with `SeekToFirst`, `SeekToLast`, `Seek`, or `SeekForPrev`, then alternate `Next` and `Prev` calls while checking visible user keys and values. The snapshot sequence passed to `DBIter::NewIter` determines which internal versions are visible.

The first tests cover `Iterator::Prepare`. Valid `MultiScanArgs` ranges are forwarded to the internal iterator exactly once, while unsorted/invalid scan ranges make the public iterator status `InvalidArgument` and do not call the child `Prepare`.

`DBIteratorPrevNext` covers direction changes and reverse iteration with repeated versions, deletions, and `iterate_upper_bound`. It checks `SeekToLast` without an upper bound, with upper bounds at existing keys, before the first key, after the last key, and around deleted keys. It also uses `PerfContext` to ensure bounded reverse seeks avoid unnecessary delete/internal-key skip accounting.

`DBIteratorEmpty`, `DBIteratorUseSkipCountSkips`, `DBIteratorUseSkip`, and `DBIteratorSkipInternalKeys` exercise empty sources, reseek optimization, large runs of duplicate versions, tombstones, and merge operands. These tests prove that `DBIter` can skip obsolete internal records, reseek when sequential skips exceed `max_sequential_skip_in_iterations`, and return `Status::Incomplete` when `ReadOptions::max_skippable_internal_keys` is exceeded. The skip counter is expected to reset after a successful visible key.

`DBIteratorTimedPutBasic` and `DBIterator1` through `DBIterator14` form a matrix over sequence visibility, merges, puts, deletes, single deletes, seek direction, and unusual keys. They check that merge operands are folded only across the visible segment up to a put or deletion boundary, that deletion/single-deletion suppresses older values as expected, and that keys containing embedded zero bytes still compare and seek correctly.

`DBIterator9` and `DBIterator10` specifically test `Seek`/`Prev` and `SeekForPrev`/`Next` direction changes. The comments preserve a historical TODO around `Seek()` followed by `Prev()` semantics, so these tests encode the current intended behavior for exact and in-between seek targets.

`DBIterWithMergeIterTest` wraps two `TestIterator` children in `NewMergingIterator`, then feeds the merged internal stream into `DBIter`. It verifies normal forward and reverse iteration, then uses `SyncPoint` callbacks at `MergeIterator::Prev:BeforePrev` to mutate a child iterator during reverse traversal. The data-race cases insert newer or out-of-range keys while `Prev()` is changing child iterator positions and assert `DBIter` still returns the stable visible sequence.

The final tests cover prefix tombstone seek behavior, lower-bound handling for `SeekToFirst`, `Prev`, and `Seek`, and a disappearing-key case where `Vanish("a")` removes the current key before a reverse-to-forward transition. That last test asserts both correctness (`Next()` lands on `b`) and a bounded number of internal iterator steps.

## State and Persistence Behavior
This file does not open an on-disk DB, write WALs, create SSTs, or persist data. All state is synthetic and process-local. The persistent semantics under test are nevertheless RocksDB read semantics: how a stable snapshot sequence number maps internal versions into user-visible values, how tombstones and single deletions mask older values, and how merge operands are accumulated around put/delete boundaries.

`TestIterator` models the internal key space by assigning increasing sequence numbers unless a test passes explicit sequence values. Since RocksDB internal ordering sorts user key ascending and sequence/type in internal-key order, `Finish()` is required before iteration. The public iterator never exposes internal keys directly; it exposes only user key/value pairs selected by `DBIter`.

Iterator state includes current direction, the saved current user key/value, status, skip counters, pinned key/value assumptions from the child iterator, and read bounds. Direction changes are central: when moving from reverse to forward or forward to reverse, `DBIter` must reposition the internal iterator without resurfacing obsolete versions or losing the next visible key.

The merge-iterator tests simulate mutable memtable-like state. `TestIterator::Add(..., update_iter=true)` can insert keys while preserving a plausible current iterator position, and `Vanish()` can remove keys lazily. These cases are not durable persistence, but they approximate the volatile state changes that a DB iterator may observe when internal child iterators refresh around compaction, filtering, or active memtables.

## Dependencies and Integration Points
The file depends on RocksDB internals in `db/db_iter.h`, `db/dbformat.h`, `table/merging_iterator.h`, and `table/iterator_wrapper.h`, public option/comparator/statistics APIs, perf context tracking, sync-point testing hooks, and the string-append merge operator from `utilities/merge_operators.h`.

The main integration point is the boundary between an `InternalIterator` over RocksDB internal records and the public `Iterator` contract. Any change in `DBIter`, internal key encoding/comparison, merge helper behavior, delete/single-delete handling, `ReadOptions` bound checks, or `NewMergingIterator` repositioning can affect these tests.

The tests also integrate with observability paths: `Options::statistics` must receive reseek ticker updates, `PerfContext` must count skipped internal keys and deletes consistently, and `Iterator::status()` must distinguish OK, `InvalidArgument`, and `Incomplete` outcomes.

## Risks
`DBIter` has high edge-case density because it combines snapshot filtering, internal-key ordering, merge folding, tombstone handling, bounds, and bidirectional cursor movement. A small repositioning change can produce duplicate user keys, skip visible keys, expose deleted values, or return incorrect merged values after direction changes.

Skip optimizations are risky because they trade linear movement for reseeks. If the skip thresholds are misapplied, iteration can become slow over many obsolete versions, counters can become misleading, or bounded-scan callers using `max_skippable_internal_keys` can miss the intended `Incomplete` failure.

Merge behavior is especially sensitive. The tests distinguish pure operand chains, operand chains terminated by puts, operand chains segmented by deletes, and chains interacting with single deletes. Incorrect operand ordering or boundary detection changes user-visible values.

Iterator bounds are another hazard. `iterate_upper_bound` and `iterate_lower_bound` must affect initial seeks and subsequent movement without leaking keys outside the requested range, including edge cases where the bound equals the first key, points to a deleted key, or lies beyond all keys.

The `SyncPoint` data-race tests depend on internal callback names and implementation timing in `MergeIterator::Prev`. Refactoring the merge iterator may require updating these tests even when the external behavior remains correct.

## Test Signals
Strong positive signals are successful runs of all `DBIteratorTest` and `DBIterWithMergeIterTest` cases with assertions on keys, values, validity, and status. The suite should show that forward and reverse iteration agree, empty iterators return invalid with OK status, and direction changes after `Seek`, `SeekForPrev`, `SeekToFirst`, and `SeekToLast` land on the expected visible keys.

Important counter signals include `NUMBER_OF_RESEEKS_IN_ITERATION` increasing in the large duplicate-version reverse scan, `internal_key_skipped_count` matching expected upper-bound seek behavior, and prefix tombstone seeks not counting skipped keys when `prefix_same_as_start` short-circuits the scan.

Important failure-status signals are `InvalidArgument` for invalid prepared scan ranges and `Incomplete` when skipped internal keys exceed `ReadOptions::max_skippable_internal_keys`. OK status after invalidation from natural iterator exhaustion is also asserted repeatedly.

Regression-sensitive scenarios include upper-bound `SeekToLast`, lower-bound `SeekToFirst` and `Prev`, timed-put values merged with operands, embedded-zero user keys, single-delete masking, current-key disappearance during reverse-to-forward movement, and merged child iterators mutated during reverse traversal.
