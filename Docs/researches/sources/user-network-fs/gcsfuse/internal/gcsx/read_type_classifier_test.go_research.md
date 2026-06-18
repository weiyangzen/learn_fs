# sources/user-network-fs/gcsfuse/internal/gcsx/read_type_classifier_test.go

## Scope

This test file validates `ReadTypeClassifier` in isolation, including helper methods and concurrent state updates.

## Purpose

The tests lock down the newer classifier heuristics that are shared across the read-manager reader chain.

## Important APIs, Types, And Functions

- Tests cover `NewReadTypeClassifier`, `isSeekNeeded`, `GetReadInfo`, `RecordSeek`, `RecordRead`, `ComputeSeqPrefetchWindowAndAdjustType`, `IsReadSequential`, `avgReadBytes`, and `GetSeeks` indirectly.
- Scenario tests model sequential reads, random reads, random-to-sequential transitions, and concurrent updates.

## Control Flow

Most tests seed atomic fields directly, call one classifier method, and assert read type, seek count, expected offset, total bytes, or returned window. Scenario tests call `RecordSeek` before reads and `RecordRead` after reads to mirror production ordering.

## State And Persistence Behavior

The tests inspect in-memory atomic state only. The concurrent test launches ten goroutines performing repeated seek/read updates and then asserts total byte accumulation and a valid final read type.

## Dependencies And Integration Points

It depends on `metrics` read-type constants, Go `sync.WaitGroup`, and testify assertions. It also uses `maxReadSize`, `minReadSize`, and `sequentialReadSizeInMb` from the gcsx test package context.

## Risks And Maintenance Notes

The tests document subtle policy choices: first non-zero offset is random, any sequential seek can switch to random, large average reads switch back to sequential, and random prefetch windows are rounded up to MB boundaries. Concurrency assertions intentionally avoid deterministic read-type expectations because update interleaving is nondeterministic.

## Test Signals

Signals include no seek when expected offset is zero, seek on backward or too-large forward sequential jumps, seek on non-contiguous random reads, no double-count when `seekRecorded` is true, expected offset update after reads, prefetch windows from 1 MiB through configured sequential size, integer-division average behavior, and exact byte totals under concurrent updates.
