# sources/user-network-fs/gcsfuse/internal/gcsx/read_type_classifier.go

## Scope

This file implements `ReadTypeClassifier`, the newer shared read-pattern classifier used by the compositional read manager and reader stack.

## Purpose

The classifier tracks expected offsets, seeks, total read bytes, initial offset, and current read type so cache, buffered, and GCS readers can make consistent sequential-vs-random decisions.

## Important APIs, Types, And Functions

- `ReadInfo` carries `ReadType`, `ExpectedOffset`, and `SeekRecorded` for one request.
- `ReadTypeClassifier` stores atomic read type, expected offset, seek count, total bytes, configured sequential read size, and initial offset.
- `NewReadTypeClassifier`, `RecordSeek`, `RecordRead`, `GetReadInfo`, `ComputeSeqPrefetchWindowAndAdjustType`, `IsReadSequential`, `NextExpectedOffset`, `avgReadBytes`, and `GetSeeks`.

## Control Flow

`GetReadInfo` snapshots state, optionally records a seek, computes average read size, and classifies as sequential when average read size is at least `maxReadSize` or no seeks have occurred and the initial offset is zero. Otherwise it classifies as random. `RecordRead` adds bytes and advances expected offset. `ComputeSeqPrefetchWindowAndAdjustType` returns configured sequential size for sequential patterns or a rounded/clamped random read window for random patterns.

## State And Persistence Behavior

All mutable state is in atomics, making the classifier safe for concurrent use. It persists only in memory for a file handle or reader lifetime; it does not write cache or remote state.

## Dependencies And Integration Points

It depends on metrics read-type constants and shares size constants with the older random-reader heuristics. `read_manager.go` creates one classifier per read manager and passes `ReadInfo` down through `ReadRequest`.

## Risks And Maintenance Notes

Classification behavior differs from the old `randomReader.getReadInfo`: a first read at non-zero initial offset can immediately classify random even before a seek. Concurrent callers get atomic consistency but not transaction-like ordering between `GetReadInfo` and `RecordRead`; tests allow final read type to vary under concurrency. Division by seeks is guarded, but average-read semantics depend on whether seeks are counted before or after reads.

## Test Signals

`read_type_classifier_test.go` validates initial state, seek detection, `GetReadInfo` and `RecordSeek`, `RecordRead`, prefetch window sizing and clamping, sequential predicate, average byte calculation, sequential and random read simulations, random-to-sequential transition after large reads, and concurrent updates.
