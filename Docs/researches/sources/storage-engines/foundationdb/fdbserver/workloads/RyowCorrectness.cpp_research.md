# sources/storage-engines/foundationdb/fdbserver/workloads/RyowCorrectness.cpp

## Purpose
`RyowCorrectnessWorkload` compares random read-your-writes transaction sequences against an in-memory key-value model. It validates that gets, ranges, selectors, key selectors, sets, clears, and range clears behave identically in an RYW transaction and the local `MemoryKeyValueStore`.

## Important APIs, Types, And Functions
The file defines an `Operation` struct with operation types `SET`, `GET`, `GET_RANGE`, `GET_RANGE_SELECTOR`, `GET_KEY`, `CLEAR`, and `CLEAR_RANGE`. `RyowCorrectnessWorkload` derives from `ApiWorkload` and registers as `RyowCorrectness`. Important methods are `generateOperationSequence`, `applySequenceToStore`, `applySequenceToDatabase`, `compareResults`, and `performTest`.

## Control Flow
Setup chooses the `READ_YOUR_WRITES` transaction factory. Each test loop generates a random sequence of `opsPerTransaction`, applies it to the memory store while collecting read results, applies the same sequence to a database transaction with retry handling, commits, then compares read outputs and final database contents against the memory model. The loop is wrapped in a timeout of `duration`.

## State And Persistence Behavior
The memory model in `ApiWorkload` tracks expected contents. Database mutations are committed transactionally. On `commit_unknown_result`, database read results already observed are retained and the transaction is retried without replacing them; on other retryable errors, collected results are cleared before `onError`.

## Dependencies And Integration Points
It depends on `ApiWorkload`, `MemoryKeyValueStore`, tester interface helpers such as `selectRandomKey`, `generateKeySelector`, `generateValue`, and `compareDatabaseToMemory`. It specifically exercises the transaction wrapper abstraction rather than raw `Transaction`.

## Risks And Edge Cases
The generated operation distribution weights reads and sets heavily but still covers selectors and range clears. Selector ranges normalize begin/end in the model when needed. The handling of `commit_unknown_result` is subtle because repeated reads could see different state; preserving first results is part of the correctness model.

## Test Signals
Failures call `testFailure` with either "Transaction results did not match" or "Database contents did not match" after printing the failed operation details. The workload has no metrics beyond inherited signals and `check` behavior from `ApiWorkload`.
