# sources/storage-engines/foundationdb/fdbserver/workloads/TimeKeeperCorrectness.cpp

## Purpose
`TimeKeeperCorrectnessWorkload` is intended to compare sampled local time-to-version observations against the database timekeeper system map, checking entry count bounds and version ordering.

## Important APIs, Types, and Functions
The workload uses `KeyBackedMap<int64_t, Version>` over `timeKeeperPrefixRange.begin`, `ReadYourWritesTransaction`, `FDBTransactionOptions::ACCESS_SYSTEM_KEYS`, `LOCK_AWARE`, and knobs `TIME_KEEPER_MAX_ENTRIES` and `TIME_KEEPER_DELAY`.

## Control Flow
`start()` logs start, records `start = now()`, and should sample read versions into `inMemTimeKeeper` until `testDuration` elapses, delaying at a fraction of `TIME_KEEPER_DELAY`. `check()` reads all timekeeper entries into a `KeyBackedRangeResult`, verifies the count does not exceed `TIME_KEEPER_MAX_ENTRIES + 1`, warns if too few entries exist, and for each database entry compares it with the first local sample at or after that time.

## State and Persistence Behavior
Database state is the system timekeeper map maintained by the cluster. Local state is `inMemTimeKeeper`, a map of sampled seconds to read versions. The workload does not write user data.

## Dependencies and Integration Points
It integrates with FoundationDB system key-backed types, the timekeeper system key range, server knobs, RYW transactions, and tester workload registration.

## Risks and Edge Cases
The `start()` loop condition is `while (now() - start > testDuration)`, which is false immediately after `start` is assigned; this appears inverted and prevents local sampling in normal execution. With an empty `inMemTimeKeeper`, `check()` can still pass without meaningful version comparisons. The version comparison flags an error when `item.second >= it->second`; the intended strictness depends on timekeeper semantics.

## Test Signals
Trace events include `TKCorrectness_Start`, `TKCorrectness_Completed`, `TKCorrectness_CheckStart`, `TKCorrectness_TooManyEntries`, `TKCorrectness_TooFewEntries`, `TKCorrectness_VersionIncorrectBounds`, and `TKCorrectness_Passed`. `check()` returns false only for too many entries or version-bound failures.
