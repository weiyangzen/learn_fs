# sources/storage-engines/rocksdb/file/random_access_file_reader_test.cc

## Purpose

`random_access_file_reader_test.cc` unit-tests `RandomAccessFileReader` direct-I/O behavior and helper interval logic. It focuses on correctness of unaligned reads, scratch copying, external allocation, multi-read alignment/merging, and helper functions.

## Important APIs, Types, and Functions

- `RandomAccessFileReaderTest` fixture creates a per-thread DB path, uses `SetupSyncPointsToMockDirectIO`, writes test files, opens readers with direct-read options, and validates request results.
- `ReadDirectIO` verifies unaligned direct-I/O reads return the requested substring when using an external aligned buffer context and both low and total rate-limiter priorities.
- `ReadDirectIOCopiesToScratch` verifies unaligned direct reads copy back into caller scratch when no direct buffer context is supplied.
- `ReadDirectIOUsesExternalBuffer` verifies an external `AlignedBuffer::Allocator` is used once with page-size alignment and that result data points into the external storage.
- `MultiReadDirectIO` validates aligned request construction and merging for multiple request layouts using the `RandomAccessFileReader::MultiRead:AlignedReqs` sync point.
- `MultiReadDirectIOUsesExternalBuffer` checks one external allocation for multiple direct-I/O requests and verifies result slices live inside that storage.
- `FSReadRequest.Align` and `FSReadRequest.TryMerge` test alignment and interval merge semantics.

## Control Flow and State

Each test writes deterministic random content, opens a random-access reader, computes the filesystem alignment, performs reads at deliberately unaligned offsets/lengths, and compares returned slices to substrings. The multi-read test captures internal aligned requests via sync point after `MultiRead` builds them, then asserts whether separate user requests collapse to one or multiple filesystem reads.

The fixture owns only test directory, env, and filesystem state. Test files are removed with `DestroyDir` in teardown.

## Dependencies and Integration Points

The tests depend on `file_util.h` for cleanup, `SetupSyncPointsToMockDirectIO`, default filesystem/env, RocksDB test harness, random data generation, and sync points. They are tightly coupled to `RandomAccessFileReader` direct-I/O internals and default page-size alignment.

## Risks and Edge Cases

- Tests skip only implicitly through mocked direct IO setup; real platform direct-I/O quirks are abstracted by test sync points.
- Expected merged intervals rely on adjacent intervals being mergeable, matching `TryMerge`'s inclusive/adjacent logic.
- External allocator tests use a no-op owner around external storage; production callers must ensure true lifetime ownership.

## Test Signals

This file provides direct regression coverage for subtle data-corruption risks in direct I/O: stale scratch data, wrong subrange extraction, incorrect merged batch offsets, and allocator misuse. It complements broader async/prefetch coverage in `prefetch_test.cc`.
