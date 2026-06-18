# sources/storage-engines/foundationdb/fdbserver/workloads/KRMCoalescingFragmentation.cpp

## Purpose
Regression workload for a `krmSetRangeCoalescing` fragmentation bug in `removeOldDestinations`. It exercises the real production KRM mutation path with a user-keyspace test prefix and verifies adjacent same-value entries are not left behind.

## Important APIs, types, and functions
`KRMCoalescingFragmentationWorkload` uses `krmSetRange`, `krmGetRanges`, `removeOldDestinations`, `serverKeysTrue`, `serverKeysFalse`, `allKeys`, and `ReadYourWritesTransaction`. Its state is `testPrefix` and `success`; the full test lives in `runTest`.

## Control flow
Client 0 initializes a KRM map to `true`, clears `["d","j")`, verifies the four-entry setup, then calls `removeOldDestinations` for current keys `["a","m")` while preserving shards `["a","c")`, `["e","g")`, and `["k","m")`. It reads the KRM back, traces all entries, detects adjacent same-value fragmentation, and asserts the exact expected transitions at empty, `"c"`, and `"k"`.

## State and persistence behavior
The workload writes KRM metadata under `KRMFragTest/` in user keyspace. It does not mutate system metadata, but it does not clean up the test prefix.

## Dependencies and integration points
Integrates directly with `KeyRangeMap` helper functions and `MoveKeys.cpp`'s `removeOldDestinations`, making it a narrow regression test for DD range-map coalescing behavior.

## Risks and test signals
Risks are hard-coded key examples and exact result-size expectations. Signals are `success`, ASSERTs on KRM entries, and `KRMFragTestFragmentationDetected`/`KRMFragTestFailed` traces when adjacent equal-value records remain.
