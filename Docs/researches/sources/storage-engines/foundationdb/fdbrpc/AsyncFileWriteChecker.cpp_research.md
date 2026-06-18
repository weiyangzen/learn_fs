# sources/storage-engines/foundationdb/fdbrpc/AsyncFileWriteChecker.cpp

## Purpose
`AsyncFileWriteChecker.cpp` defines static storage for the write-checker wrapper and contains a focused unit test for its LRU checksum-history data structure.

## Important APIs, Types, and Functions
It initializes `AsyncFileWriteChecker::checksumHistoryBudget` and `checksumHistoryPageSize`. `compareWriteInfo` asserts equality of timestamp/checksum pairs. The local `LRU2` reference implementation uses a linked list plus unordered map to model expected LRU behavior. The test case `/fdbrpc/AsyncFileWriteChecker/LRU` compares the production `LRU` against `LRU2`.

## Control Flow
The test runs 1000 randomized operations. Each iteration either updates a random page with a new checksum/timestamp, removes a random existing page, or truncates at a random page. After each operation it checks existence, stored write info, and least-recently-used page agreement between the production and reference implementations.

## State and Persistence Behavior
The file owns process-static checker budget and page size defaults. Test state is transient and uses deterministic randomness. It does not touch disk directly; persistence behavior belongs to the header implementation wrapping `IAsyncFile`.

## Dependencies and Integration Points
The file depends on `AsyncFileWriteChecker.h` and `flow/UnitTest.h`. The test integrates with the FoundationDB unit-test runner and validates the helper used by the runtime checker.

## Risks and Edge Cases
The LRU test validates metadata behavior but not actual asynchronous file read/write verification. It uses deterministic random coverage over a small page range, so it can miss pathological map-order or truncation cases. `LRU2::truncate` is intentionally linear in page number and only suitable for test-sized ranges.

## Test Signals
Passing `/fdbrpc/AsyncFileWriteChecker/LRU` indicates update/remove/truncate/least-recent behavior matches the reference model. It does not validate checksum failure detection, sync-time gating, global budget exhaustion, or interaction with concurrent file writes.
