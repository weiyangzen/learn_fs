# sources/storage-engines/foundationdb/fdbserver/workloads/Unreadable.cpp

## Purpose
`UnreadableWorkload` fuzzes read-your-writes unreadable-range behavior caused by versionstamped atomic operations. It compares expected unreadable regions in a local model with transaction results for gets and range reads.

## Important APIs, Types, and Functions
The workload uses `ReadYourWritesTransaction`, `KeyRangeMap<bool>`, `RandomTestImpl` key/value/range helpers, `MutationRef::SetVersionstampedValue`, `MutationRef::SetVersionstampedKey`, `getVersionstampKeyRange()`, `FDBTransactionOptions::BYPASS_UNREADABLE`, `SNAPSHOT_RYW_DISABLE`, and `SNAPSHOT_RYW_ENABLE`. Static helpers include `containsUnreadable()`, `resolveKeySelector()`, and `checkUnreadability()`.

## Control Flow
Only client 0 runs `_start()`. For 100 test transactions, it creates a local `setMap` containing normal-key sentinels and a `KeyRangeMap` of unreadable regions, optionally enables bypass unreadable, then performs 500 random operations: sets, conflict ranges, clears, versionstamped value/key atomic ops, range reads by key range, range reads by key selectors, and point gets. For read operations it captures either results or `accessed_unreadable`, accounts for snapshot mode and bypass behavior, and asserts that the local unreadable model predicts the outcome. Unexpected errors reset the transaction and local model.

## State and Persistence Behavior
The workload performs writes and atomic operations in a RYW transaction but does not explicitly commit in `_start()`, so the main target is client-side transactional state before commit. Local model state is reset on unexpected transaction errors.

## Dependencies and Integration Points
It integrates with RYW transaction internals, versionstamp mutation semantics, key selector resolution, normal/all key ranges from tester utilities, and random workload helper functions.

## Risks and Edge Cases
`resolveKeySelector()` assumes the sentinel keys exist and manipulates iterators near begin/end; the code includes explicit exceptions for RYW optimization cases where a query may be conservatively unreadable. Because many cases are intentionally skipped as acceptable, coverage is nuanced rather than a direct equality model for every selector. `check()` always returns true and failures are assertion-driven.

## Test Signals
Assertions in `checkUnreadability()` and operation checks are the main signal. There are commented trace probes for debugging model mismatches. Successful completion of `_start()` implies the local unreadability model matched observed RYW behavior across fuzz operations.
