# sources/sync-backup/syncthing/lib/scanner/blocks_test.go

## Purpose
Unit tests and benchmark for block hash generation and validation.

## Important APIs, Types, and Functions
`blocksTestData` defines input data, block size, and expected hex hashes. `TestBlocks` exercises `Blocks`. `BenchmarkValidate` exercises `Validate` over random 128 KiB buffers.

## Control Flow
`TestBlocks` loops over table entries, hashes each buffer with no size hint, verifies the number of blocks, then checks offsets, block sizes, and expected hash strings for each block. The benchmark precomputes valid random blocks and repeatedly validates them.

## State and Persistence Behavior
All test data is in memory. No persistence or filesystem access.

## Dependencies and Integration Points
Depends on `bytes`, `context`, `crypto/sha256`, `fmt`, `math/rand`, and `testing`. It validates low-level scanner output that feeds protocol indexes.

## Risks and Edge Cases
The test checks known hashes for small examples but does not exercise context cancellation, size hints, counters, or read errors. The benchmark uses deterministic pseudo-random data, which is fine for performance tests.

## Test Signals
Passing tests prove block splitting, offsets, lengths, empty-file handling, and SHA-256 digest generation match expected values.
