# sources/storage-engines/foundationdb/fdbserver/workloads/ApiCorrectness.cpp

## Purpose
`ApiCorrectness.cpp` implements the `ApiCorrectness` tester workload. It validates FoundationDB transaction APIs by comparing real database behavior against an in-memory `MemoryKeyValueStore` model for sets, gets, range reads, key-selector range reads, key resolution, point clears, and range clears.

## Important APIs, Types, and Functions
- `OperationType`: `SET`, `GET`, `GET_RANGE`, `GET_RANGE_SELECTOR`, `GET_KEY`, `CLEAR`, `CLEAR_RANGE`.
- `ApiCorrectnessWorkload : ApiWorkload`: workload type registered through `WorkloadFactory`.
- Options include operation counts, `minSizeAfterClear`, `maxRandomTestKeys`, `randomTestDuration`, `maxTransactionBytes`, and `resetDBTimeout`.
- `performSetup`: chooses a random API wrapper from NativeAPI, ReadYourWrites, ThreadSafe, and MultiVersion.
- `performTest`: runs scripted coverage, resets the DB, then runs timed random operations.
- Helpers `runSet`, `runGet`, `runGetRange`, `runGetRangeSelector`, `runGetKey`, `runClear`, and `runClearRange` perform the actual validation.

## Control Flow
Setup selects the transaction implementation. The scripted phase sets generated data, validates point and range reads, validates key selectors, clears points, and clears ranges. Range-clear tests restore original data when the model drops below `minSizeAfterClear`. If scripted checks pass, the workload resets the database using `runSet`, then enters `runRandomTest` until the configured timeout. Random operation probabilities depend on current model size so the test tends to add data when sparse and clear data when dense.

Each helper creates retry-aware `TransactionWrapper` instances, chunks work by `maxKeysPerTransaction`, calls `transaction->onError` on retryable failures, updates the memory model after successful writes/clears, and compares real reads against the model. Range-selector validation carefully handles per-client prefix boundaries and `0xff` keyspace filtering.

## State and Persistence Behavior
The persistent database state is the per-client prefix inherited from `ApiWorkload`. The expected state is `store`, an in-memory `MemoryKeyValueStore`. `success` is the pass/fail latch. The generated `data` vector grows during random sets and is used as a source of likely-existing keys. Write and clear paths deliberately add read conflict ranges to make test transactions self-conflicting and reduce ambiguity.

## Dependencies and Integration Points
The workload depends on `ApiWorkload.h`, `MemoryKeyValueStore`, `ManagementAPI`, `MutationTracking`, simulator deterministic random, Flow actors, and tester workload registration. It integrates with transaction retry semantics through `TransactionWrapper::onError` and with all transaction implementations selected by `ApiWorkload::chooseTransactionFactory`.

## Risks
Selector-boundary handling is subtle and likely to expose both real regressions and test assumptions. Large configured key/value sizes can exceed transaction-size expectations unless `maxKeysPerTransaction` remains conservative. `runClearRange` updates memory before the DB commit and relies on retry semantics preserving the eventual operation. Random density math controls coverage balance and can starve operation classes if changed incorrectly.

## Test Signals
Failures call `testFailure`, producing stdout and `TraceEvent(SevError, "TestFailure")`. Metrics include `Number of Random Operations Performed`. Mutation debug macros emit `ApiCorrectnessSet` and `ApiCorrectnessClear`. Range comparison failures include detailed DB/memory dumps and read versions.
