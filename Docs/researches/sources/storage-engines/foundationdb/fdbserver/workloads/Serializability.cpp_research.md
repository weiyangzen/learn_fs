# sources/storage-engines/foundationdb/fdbserver/workloads/Serializability.cpp

## Purpose
`SerializabilityWorkload` compares two executions of randomly generated transaction groups to detect violations in transactional serialization, RYW behavior, conflict handling, watches, atomic operations, and range/key reads.

## Important APIs, Types, And Functions
The workload derives from `TestWorkload` and registers as `Serializability`. It defines `GetRangeOperation`, `GetKeyOperation`, `GetOperation`, and `TransactionOperation`. Important methods are `randomTransaction`, `runTransaction`, `getDatabaseContents`, `resetDatabase`, and `_start`.

## Control Flow
Client 0 repeatedly generates initial data and three random transactions `a`, `b`, and `c`. It first resets the database, runs and commits `a`, then `b`, then `c`, and captures contents. It resets again, runs `a` and `b` in a single transaction, runs `c` in another transaction, commits both, then compares final contents and all deterministic read futures. Snapshot reads in transaction `c` can be masked with `dontCheck` because they may legitimately differ across schedules.

## State And Persistence Behavior
Each iteration clears `normalKeys` and writes generated initial data before executing test schedules. Mutations include sets, range clears, single-key clears, atomic ops, explicit read/write conflict ranges, and watches. Reads are stored as futures so later comparisons observe the actual completed results.

## Dependencies And Integration Points
It depends on NativeAPI, `ReadYourWritesTransaction`, actor collections, tester workload helpers, mutation types, key selectors, and watch APIs. It exercises both read and write transaction paths with randomized waiting between operations.

## Risks And Edge Cases
The workload uses assertions for mismatches and does not set `success=false`, so assertion failure is the primary error path. Snapshot-read masking is intentionally selective; incorrect masking could hide or expose nondeterminism. Watch futures are created but not compared, serving mainly as operations affecting transaction behavior.

## Test Signals
Mismatches emit `SRL_ResultMismatch`, `SRL_Result1`, and `SRL_Result2` traces before asserting. The configuration trace reports node count, key layout, value sizes, and clear size. `check` returns the `success` flag, which remains true unless changed by future edits.
