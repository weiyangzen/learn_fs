# sources/storage-engines/foundationdb/fdbserver/workloads/ApiWorkload.cpp

## Purpose
`ApiWorkload.cpp` implements shared behavior for API tester workloads. It prepares a per-client keyspace, generates randomized test keys and values, chooses a transaction API implementation, compares database ranges with an in-memory model, and exposes setup/start/check/failure helpers for subclasses.

## Important APIs, Types, and Functions
- `ApiWorkload::setup` and helper `setup`: set a default native transaction factory, clear the client keyspace, then call subclass `performSetup`.
- `ApiWorkload::start` and helper `start`: generate short-key and long-key data under the client prefix, then call subclass `performTest`.
- `clearKeyspace`: clears `[clientPrefixInt, clientPrefixInt + 1)` with transaction retries.
- `testFailure`: prints/traces a failure and sets `success = false`.
- `compareResults` and `compareDatabaseToMemory`: validate real range results against `MemoryKeyValueStore`.
- Random helpers: `generateData`, `generateKey`, `generateKeySelector`, `selectRandomKey`, `generateValue`.
- `chooseTransactionFactory`: selects Native, ReadYourWrites, ThreadSafe, or MultiVersion wrappers.

## Control Flow
Participating clients clear their prefix during setup, then run subclass setup. Start builds a mixed short/long key dataset and invokes subclass test logic. Comparison scans `[clientPrefix, clientPrefix + "\xff")` in 100-row chunks, using a transaction wrapper for the real database and `store.getRange` for the model. Transaction factory selection creates Flow wrappers for Native/RYW, thread-safe wrappers for `ITransaction`, or multi-version debug wrappers through `MultiVersionDatabase`.

## State and Persistence Behavior
The persistent surface is the per-client key prefix in the database. The expected state is the `store` member owned by `ApiWorkload`. `success`, `transactionFactory`, and `transactionType` are runtime state. In simulation, `useExtraDB` and `extraDB` allow Flow transaction wrappers to switch between the main database and one configured extra simulated database after errors.

## Dependencies and Integration Points
The file depends on `ApiWorkload.h`, `FDBTypes`, `MultiVersionTransaction`, simulator policy state, Flow arena/reference utilities, deterministic random, and `fmt`. It integrates with `ThreadSafeDatabase::createFromExistingDatabase`, `MultiVersionApi::selectApiVersion`, and subclass hooks `performSetup`/`performTest`.

## Risks
Binary random key generation uses a NUL-terminated char buffer and string concatenation, so embedded NUL bytes truncate entropy. `compareDatabaseToMemory` continuation behavior depends on real and memory range semantics remaining aligned. Formatted decimal prefixes must remain lexicographically non-overlapping. Multi-version and thread-safe bridges may expose bugs only when that transaction mode is randomly selected.

## Test Signals
Failure traces include `TestFailure`, `*_CompareSizeMismatch`, `*_CompareValueMismatch`, and `FailedComparisonToMemory`, with stdout range dumps. Transaction-mode selection prints the chosen API. `check` returns the `success` latch.
