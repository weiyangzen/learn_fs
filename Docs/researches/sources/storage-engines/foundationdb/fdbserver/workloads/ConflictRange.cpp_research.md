# sources/storage-engines/foundationdb/fdbserver/workloads/ConflictRange.cpp

## Purpose
`ConflictRange.cpp` defines `ConflictRange`, a workload that stress-tests range read conflict behavior, key selectors, limits, reverse reads, and read-your-writes interactions. It compares whether a transaction that conflicts with a range read produces changed results, and whether a non-conflicting transaction preserves the original range result.

## Important APIs, Types, And Functions
The main type is `ConflictRangeWorkload : TestWorkload`, with actor `conflictRangeClient`. It uses `Transaction`, `ReadYourWritesTransaction`, `KeySelectorRef`, `getRange`, `setVersion`, `not_committed`, `timeKeeperSetDisable`, and metrics `withConflicts`, `withoutConflicts`, and `retries`.

## Control Flow
Client 0 disables the timekeeper in simulation, repeatedly initializes a numeric keyspace with random present keys plus a sentinel, generates a non-empty random range read, optionally performs a read-your-writes clear/set setup, creates transactions at the same read version, mutates random existing or absent keys in one transaction, commits it, then performs the generated range read and commit in the other transaction. If it gets `not_committed`, it re-reads and expects changed results except for documented selector/limit/sentinel edge cases. If it commits, it expects the new result to match the original result.

## State And Persistence
Persistent state is the test keyspace of zero-padded numeric keys and a sentinel just past the range. Each iteration clears/reinitializes the range and commits random mutations. Runtime state tracks inserted and cleared integer sets plus original range results.

## Dependencies And Integration Points
The workload depends on FDB conflict range semantics, key selector resolution, read-your-writes transaction behavior, and simulation timekeeper controls. It disables `RandomRangeLock` because range-lock transactions create unrelated conflicts.

## Risks
The constructor appears to read `maxOperationsPerTransaction` using the `"minOperationsPerTransaction"` option name, so the max option cannot be independently configured as written. Several expected-conflict edge cases deliberately throw `not_committed` to discard ambiguous cases where results do not change. The test assumes the keyspace remains outside system keys using the sentinel check.

## Test Signals
Metrics count `WithConflicts`, `withoutConflicts`, and `Retries`. Failure traces are `ConflictRangeError` and `ConflictRangeDump`, with detailed selector parameters and original/current results. A healthy run continually alternates conflict and non-conflict cases without SevError traces.
