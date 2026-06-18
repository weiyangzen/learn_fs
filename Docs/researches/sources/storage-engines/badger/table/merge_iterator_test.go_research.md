# sources/storage-engines/badger/table/merge_iterator_test.go

## Purpose
This file tests duplicate suppression, ordering, seeking, reversal, nesting, and ownership semantics for `MergeIterator`.

## Important Tests and Helpers
- `SimpleIterator` is a minimal `y.Iterator` implementation with configurable reverse behavior and global close counting.
- `newSimpleIterator`, `getAll`, `reversed`, and `closeAndCheck` support compact assertions.
- `TestSimpleIterator`, `TestMergeSingle`, and `TestMergeSingleReversed` verify baseline iterator behavior and single-iterator passthrough.
- `TestMergeMore`, `TestMergeIteratorNested`, and `TestMergeIteratorDuplicate` cover multiple iterators, nested merge construction, and duplicate winner semantics.
- `TestMergeIteratorSeek`, `TestMergeIteratorSeekReversed`, and invalid variants validate seek boundaries.
- `TestMergeDuplicates` stresses repeated duplicate keys in every child.

## Control Flow and State Behavior
The tests build ordered key/value slices, call `NewMergeIterator`, position with `Rewind` or `Seek`, then drain with `getAll`. For duplicate cases, expected values encode which iterator should win. Reverse tests mutate `SimpleIterator.reversed` and expect descending keys with corresponding winner changes. Close tests verify that the merge iterator owns and closes every underlying iterator.

## Dependencies and Integration Points
The file uses `testify/require`, `sort`, `testing`, and Badger `y` helpers. Its simple iterator implements exactly the public iterator contract consumed by the merge logic, making it independent of table storage.

## Risks and Edge Cases
The tests focus on string keys at timestamp zero, so they do not separately exercise timestamp ordering beyond `y.KeyWithTs`. They do not call `Valid` before positioning, which matches expected use. Because `closeCount` is global, tests are structured serially rather than parallel.

## Test Signals
The suite gives clear evidence that merge iteration suppresses duplicates, preserves direction, handles invalid seeks, closes owned children, and respects iterator input order for conflict resolution.
