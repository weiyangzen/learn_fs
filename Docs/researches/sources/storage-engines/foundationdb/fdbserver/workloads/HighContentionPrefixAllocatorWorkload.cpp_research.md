# sources/storage-engines/foundationdb/fdbserver/workloads/HighContentionPrefixAllocatorWorkload.cpp

## Purpose
Correctness workload for `HighContentionPrefixAllocator`, verifying that many concurrent allocator calls return unique, non-overlapping prefixes and write only inside the allocator subspace.

## Important APIs, types, and functions
`HighContentionPrefixAllocatorWorkload` owns a `Subspace("test_subspace")`, `HighContentionPrefixAllocator`, allocation counters, and a `std::set<Key>` of allocated prefixes. `runAllocationTransaction` issues multiple `allocator.allocate(tr)` calls in one `ReadYourWritesTransaction`; `runTest` runs randomized rounds of concurrent allocation transactions; `check` verifies counts and key bounds.

## Control flow
For each round, the workload starts a random number of allocation transactions. Each transaction chooses a random allocation count, waits for all allocation futures, commits, then checks the returned prefixes against previously allocated prefixes for exact duplicates or prefix containment in either direction. Check reads the first and last keys in the database to ensure all writes are within the allocator subspace.

## State and persistence behavior
The allocator persists its internal state beneath `allocatorSubspace`. The workload also maintains in-memory expected counts and the set of allocated prefixes. It does not clear the subspace.

## Dependencies and integration points
Depends on `fdbclient/HighContentionPrefixAllocator.h`, tuple/subspace key layout, `ReadYourWritesTransaction`, and tester concurrency primitives.

## Risks and test signals
The in-memory `expectedPrefixes` increments before transaction success but each transaction runs until commit, so cancellation or unexpected failure would skew counts. The key-bound check assumes the database contains no unrelated keys. Signals are ASSERTs and `HighContentionAllocationWorkloadFailure` traces for prefix collisions, wrong allocation count, or keys outside the subspace.
