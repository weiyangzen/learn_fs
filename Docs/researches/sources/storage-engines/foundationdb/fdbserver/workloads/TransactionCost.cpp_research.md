# sources/storage-engines/foundationdb/fdbserver/workloads/TransactionCost.cpp

## Purpose
`TransactionCostWorkload` validates transaction cost accounting used by tag throttling. It runs randomized read, write, clear, and range-read cases and asserts the final transaction cost matches expected knob-derived values.

## Important APIs, Types, and Functions
The workload defines nested `ITest` implementations: `ReadEmptyTest`, `ReadLargeValueTest`, `WriteTest`, `WriteLargeValueTest`, `WriteMultipleValuesTest`, `ClearTest`, `ReadRangeTest`, `ReadMultipleValuesTest`, and `LargeReadRangeTest`. It uses `ReadYourWritesTransaction::getTotalCost()`, `CLIENT_KNOBS->TAG_THROTTLING_PAGE_SIZE`, `TAG_THROTTLING_RW_FUNGIBILITY_RATIO`, binary key encoding with `bigEndian64`, and optional `debugTransaction()`.

## Control Flow
Client 0 runs `runTests()`. For each iteration, `createRandomTest()` selects one nested test. `runTest()` runs any setup writes, creates a RYW transaction, optionally assigns a debug ID, executes the test's operations, commits, and asserts `tr->getTotalCost()` equals `expectedFinalCost()`. Errors retry through `tr->onError()`.

## State and Persistence Behavior
Database state is namespaced under configurable `prefix` plus encoded test number and index. Setup phases create data for large value and range read tests. Test writes/clears persist; the workload does not clean them up.

## Dependencies and Integration Points
It integrates with RYW transaction cost tracking, client knobs, tester workload registration, Flow actors, and debug transaction tracing.

## Risks and Edge Cases
Expected costs are tightly coupled to tag-throttling page-size and fungibility constants. Changes in accounting semantics can break assertions even if client behavior remains correct. `runTests()` declares an unused `Future<Void> f`; this is harmless. Because data is not cleared, repeated runs with the same prefix can observe previous state only through tests that read keys they set up by test number.

## Test Signals
The key signal is `ASSERT_EQ(tr->getTotalCost(), test->expectedFinalCost())`. `check()` always returns true after start completes, so mismatches fail via assertion.
