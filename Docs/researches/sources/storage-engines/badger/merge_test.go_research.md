<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/merge_test.go -->
# sources/storage-engines/badger/merge_test.go

## Purpose
This file tests the merge operator API and its interaction with deletes, stopping, and LSM compaction cleanup.

## Important APIs, Types, And Functions
`TestGetMergeOperator` contains subtests for get-before-add, add/get, byte-slice append, get before background compaction, delete reset, get after stop, and old-key cleanup. Helpers `uint64ToBytes`, `bytesToUint64`, and `add` encode/decode big-endian counters and implement sum merging.

## Control Flow
Tests create a merge operator, call `Add` several times, call `Get`, and compare merged output. Some subtests stop the operator to force final compaction. The cleanup test writes thousands of merge entries, closes with `CompactL0OnClose`, reopens, then iterates all versions for the merge key and expects one remaining version.

## State And Persistence Behavior
The tests cover merge values stored as Badger versions, delete tombstone behavior, final compaction on `Stop`, and persistent LSM compaction cleanup across close/reopen.

## Dependencies And Integration Points
It uses `runBadgerTest`, `Open`, `getTestOptions`, `CompactL0OnClose`, transactions, iterators with `AllVersions`, and the merge API from `merge.go`.

## Risks And Edge Cases
Timer-based background compaction can make tests sensitive to timing, though most assertions use synchronous `Get` or `Stop`. The old-key cleanup test depends on close-time L0 compaction behavior and exact one-version cleanup.

## Test Signals
Signals include `ErrKeyNotFound` before writes, correct merged values, reset after delete, valid get after `Stop`, and only one persisted version after forced compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/merge_test.go -->
