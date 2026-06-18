# sources/storage-engines/foundationdb/bindings/c/test/performance_test.c

## Purpose
`performance_test.c` is a C API benchmark program that measures local-client throughput for common FoundationDB operations and writes KPI/error results through `test.h`.

## Important APIs, Types, and Functions
- Globals configure `numKeys`, `keySize`, generated `keys`, `valueSize`, and `valueStr`.
- `waitError`, `run`, `runTest`, and `runTestDb` provide retry and median-measurement harnesses.
- Setup helpers `clearAll`, `insertRange`, and `insertData` prepare the keyspace.
- Benchmarks include `futureLatency`, `clear`, `clearRange`, `set`, `parallelGet`, `alternatingGetSet`, `serialGet`, `getRange`, `getKey`, `getSingleKeyRange`, and `writeTransaction`.
- `runTests` opens the database/network, loads data, runs all KPIs, and stops the network.

## Control Flow
`main` selects the API version, allocates a fixed value buffer and one million generated keys, runs the benchmark suite, writes a result JSON file, and frees resources. Each benchmark is run 25 times; the median throughput is recorded. Most transaction benchmarks execute inside `run`, which retries via `fdb_transaction_on_error` and commits if the operation function succeeds.

## State and Persistence Behavior
The benchmark clears the entire database keyspace and loads one million keys, so it is destructive to the target cluster. Some mutation benchmarks reset the transaction before commit to avoid changing loaded data. Results are persisted as `fdb-c_result-<random>.json`.

## Dependencies and Integration Points
It uses the FoundationDB C API, generated options, pthread-based network thread helpers from `test.h`, and C heap allocation. The KPI names are consumed by surrounding performance infrastructure.

## Risks
The test is destructive because `clearAll` clears `["", "\xff")`. Error paths in some loops destroy only the current future and can leak other allocated futures. Large key allocation and one-million-key load make runtime and memory cost high. The benchmark uses wall-clock timing and `rand()`, so results are noisy.

## Test Signals
Successful output includes KPIs for each named operation and no errors in the result file. Correctness checks in range benchmarks validate expected counts and no extra pages for exact single-key range reads.
