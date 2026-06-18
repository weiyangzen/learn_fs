# sources/storage-engines/rocksdb/db/multi_cf_iterator_test.cc

## Purpose
`multi_cf_iterator_test.cc` is the behavioral test suite for RocksDB's multi-column-family iterator APIs. It verifies `DB::NewCoalescingIterator` and `DB::NewAttributeGroupIterator` across duplicate keys, column-family priority, forward/reverse movement, bounds, snapshots, custom comparators, wide columns, and deferred value preparation.

## Important APIs, Types, And Functions
`CoalescingIteratorTest` extends `DBTestBase` and provides `VerifyCoalescingIterator`, which checks `SeekToFirst`/`Next` and `SeekToLast`/`Prev` against expected keys, values, and optional wide columns. `VerifyExpectedKeys` verifies the natural order of a single column-family iterator.

`AttributeGroupIteratorTest` similarly provides `VerifyAttributeGroupIterator`, checking `AttributeGroupIterator::attribute_groups()` and deferred `PrepareValue`.

The tests use public APIs including `NewCoalescingIterator`, `NewAttributeGroupIterator`, `Put`, `PutEntity`, `GetSnapshot`, `ReleaseSnapshot`, `Flush`, `CompactRange`, `Iterator::PrepareValue`, `Iterator::columns`, `AttributeGroups`, `IteratorAttributeGroups`, wide-column helpers, and RocksDB sync points.

## Control Flow
The coalescing tests start with invalid input (`NewCoalescingIterator` with no column families), then cover simple values. Unique keys across column families must produce globally sorted keys independent of supplied CF order. Duplicate keys must collapse to one result; the chosen scalar value follows the priority implied by the caller's CF handle order.

Bounds tests repeat unique-key and duplicate-key scenarios with inclusive lower bounds and exclusive upper bounds, including explicit `Seek` and `SeekForPrev` calls around the bounds. Snapshot tests install sync-point dependencies so a flush or update races with multi-CF snapshot acquisition, then verify explicit snapshots see old values and implicit snapshots see a consistent current view.

Wide-column tests insert `AttributeGroups` with overlapping column names and verify coalesced columns. Some columns are merged, and overlapping non-default columns resolve according to CF order. Comparator tests ensure a coalescing iterator rejects column families with different comparator names/orders while accepting independently allocated but semantically identical custom comparators.

The unprepared-value tests enable blob files and `ReadOptions::allow_unprepared_value`. They expect values or attribute groups to be empty before `PrepareValue`, then populated after successful preparation. One test tampers with blob-index data through a sync point and expects `PrepareValue` to return false, invalidate the iterator, and expose corruption.

## State And Persistence Behavior
The tests create real column families, memtables, SSTs, and blob files. Flushes move data into persistent table/blob files so deferred value preparation exercises storage-backed reads, not only memtable values. Snapshot tests verify visibility across flushes and compactions while an iterator is being created or used.

For duplicate keys, persistent state can contain several values or wide-column groups under the same user key in different column families. The multi-CF iterator exposes one logical entry per key, with conflict resolution determined by the supplied handle order and by column-name coalescing rules.

## Dependencies And Integration Points
The file depends on `db/db_test_util.h`, `db/wide/wide_column_test_util.h`, `rocksdb/attribute_groups.h`, SyncPoint instrumentation, comparator test utilities, blob-file support, and DBTestBase helpers.

Integration points include `DBImpl` multi-CF snapshot creation, child iterator bounds, blob reader `PrepareValue`, wide-column serialization, custom comparator identity/name checks, and auto-refresh with snapshots during compaction.

## Risks
The most important correctness risk is equal-key coalescing. Scalar values and overlapping wide columns intentionally depend on CF handle order, so a heap tie-breaker or population-order bug can produce stable but wrong values.

Snapshot races are subtle. The tests use sync points to force updates between version references and snapshot checks; a change in snapshot acquisition order could reintroduce inconsistent cross-CF views. Deferred value mode must not expose stale empty values after `PrepareValue`, and corruption during blob preparation must not leave the iterator apparently valid.

Comparator compatibility is another risk. Accepting truly different comparators would break global ordering, while rejecting distinct instances of the same comparator would be unnecessarily strict.

## Test Signals
Success signals include expected `IterStatus` strings for seek/advance operations, exact key/value vectors in both traversal directions, invalid-argument statuses for bad CF lists or mixed comparators, expected wide-column sets, old/new snapshot visibility, empty pre-`PrepareValue` values followed by correct populated values, corruption status after blob tampering, and valid attribute-group iteration before and after blob-backed flushes.
