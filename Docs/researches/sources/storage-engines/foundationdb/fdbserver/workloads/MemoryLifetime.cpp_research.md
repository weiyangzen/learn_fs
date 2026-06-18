# sources/storage-engines/foundationdb/fdbserver/workloads/MemoryLifetime.cpp

## Purpose
Workload that checks returned memory from transaction read APIs remains valid across transaction object replacement and short delays. It repeatedly performs equivalent reads and compares the retained results.

## Important APIs, types, and functions
`MemoryLifetime` derives from `KVWorkload`, uses `bulkSetup`, random keys/selectors, `ReadYourWritesTransaction`, `getRange`, `get`, `getKey`, and `getAddressesForKey`. It overrides `operator()` for bulk setup and runs all checks in `start`.

## Control flow
Setup bulk-loads `nodeCount` random key/value pairs. Start loops until `testDuration`, randomly choosing one of four operations. For range/get/key-selector checks, it may add a local write in the transaction, performs the read with random snapshot/reverse options, replaces the transaction, waits 0.01 seconds, repeats the same local write and read, then asserts both results match. For address lookups, it validates retained address strings parse successfully.

## State and persistence behavior
Setup writes normal test data through `bulkSetup`; the repeated local transaction writes are not committed. Runtime state is only local comparisons.

## Dependencies and integration points
Depends on RYW transaction memory ownership, snapshot and reverse range APIs, address-for-key lookup, deterministic random workload helpers, and bulk setup.

## Risks and test signals
The workload is designed to catch lifetime/arena bugs rather than data-model bugs. It can be sensitive to real data changes between paired reads, but local uncommitted mutations are replayed. Signals are ASSERTs and detailed `MemoryLifetimeCheckKeyError`/`MemoryLifetimeCheckValueError` traces.
