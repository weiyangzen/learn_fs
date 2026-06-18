# sources/storage-engines/badger/y/y_test.go

## Purpose
This file tests and benchmarks core `y` utilities, especially `PageBuffer`, `ValueStruct` size math, allocator-backed protobuf allocation, and `SafeCopy` edge behavior.

## Important APIs, Types, And Functions
`BenchmarkBuffer` compares `bytes.Buffer` and `PageBuffer`. Page-buffer tests cover writes, truncation, readers from fixed/random offsets, chunked reads, oversized read buffers, and zero-length reads. `TestSizeVarintForZero`, `TestEncodedSize`, `TestAllocatorReuse`, and `TestSafeCopy_Issue2067` cover other helpers.

## Control Flow
Tests write random bytes into `PageBuffer`, mirror operations in `bytes.Buffer` or raw slices, and compare `Bytes`/reader output. Allocator reuse repeatedly resets a `z.Allocator`, builds many `pb.KV` entries, and marshals them.

## State And Persistence Behavior
All tests are in-memory. They protect structures used to buffer serialized data that can later be persisted.

## Dependencies And Integration Points
They depend on `bytes`, `binary`, `io`, protobuf marshal, Badger `pb`, Ristretto allocator, and `testify/require`.

## Risks And Edge Cases
Random test data changes per run but assertions are deterministic over mirrored data. Tests do not cover all unsafe byte conversion helpers or `Throttle`.

## Test Signals
Failures indicate broken paged buffer boundary handling, EOF behavior, varint encoded size calculation, allocator object layout, or `SafeCopy` compatibility with callers expecting non-nil empty slices.
