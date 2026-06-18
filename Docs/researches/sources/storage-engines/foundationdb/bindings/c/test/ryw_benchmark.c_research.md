# sources/storage-engines/foundationdb/bindings/c/test/ryw_benchmark.c

## Purpose
`ryw_benchmark.c` measures read-your-writes cache performance in a single FoundationDB C transaction after loading keys into the transaction's local state.

## Important APIs, Types, and Functions
- `insertData` clears the keyspace and sets `numKeys + 1` keys in one transaction.
- `runTest` runs a transaction-local benchmark 25 times and records median keys/sec.
- Benchmarks include `getSingle`, `getManySequential`, `getRangeBasic`, `singleClearGetRange`, `clearRangeGetRange`, and `interleavedSetsGets`.
- `runTests` opens the database, creates one transaction, obtains a read version, populates local mutations, runs benchmarks, and tears down.

## Control Flow
Unlike `performance_test.c`, benchmarks generally reuse one transaction and rely on the transaction's local RYW cache. Range benchmarks validate returned counts after local clears and clear ranges, then repopulate transaction state with `insertData`.

## State and Persistence Behavior
The test mutates a transaction's local state heavily. It does not explicitly commit after `insertData`, so most measured behavior is transaction-local rather than durable cluster state. It still issues a full clear and sets inside the transaction, and results are persisted through `writeResultSet`.

## Dependencies and Integration Points
It depends on the FDB C API, `test.h` result/network helpers, and generated key arrays. It is part of C binding benchmark coverage for RYW cache behavior.

## Risks
Several error paths return without destroying the current future, and `getRangeBasic` does not destroy futures in the success path. The code expects exact range counts from local mutations and may be sensitive to API semantics. `insertData` iterates `<= numKeys`, which relies on `generateKeys` allocating `numKeys + 1`.

## Test Signals
Result JSON should contain six RYW KPI names and no errors. Count checks in range benchmarks are direct correctness signals for local clear and clear-range visibility.
