# sources/storage-engines/foundationdb/fdbserver/workloads/Mako.cpp

## Purpose
Configurable benchmark workload for mixed FoundationDB operations. It can bulk-populate key/value data, run user-specified transaction mixes, record per-operation latency and throughput, optionally maintain checksum keys for consistency validation, and clean up benchmark data.

## Important APIs, types, and functions
`MakoWorkload` parses an operation spec into `operations[MAX_OP][2]` across GRV, get, range get, snapshot get, update, insert, insert range, clear, set-clear, clear range, set-clear-range, and commit. It uses `bulkSetup`, `ReadYourWritesTransaction`, `DDSketch`, `PerfIntCounter`, Zipf generators, CRC32C helpers, checksum keys, and operation counters. Key methods include `keyForIndex`, `randomValue`, `parseOperationsSpec`, `_setup`, `_runBenchmark`, `makoClient`, checksum calculation/update/verification, `tracePeriodically`, and `cleanup`.

## Control flow
Setup optionally bulk-loads rows and, on client 0, generates checksum keys. Start runs `actorCountPerClient` Poisson-paced clients for `testDuration`, optionally with periodic trace logging. Each client loops through configured operation counts, chooses random or Zipf-distributed keys, performs reads/writes/ranges, marks checksum partitions affected by mutations, commits when required, updates per-op counters and latency sketches, and retries on transaction errors while counting conflicts. Check verifies all configured checksum keys by recomputing CRC32C over sampled rows.

## State and persistence behavior
Benchmark data is stored under the configurable key prefix with fixed-length keys and random values. Optional checksum keys are named from the prefix and row count and are updated in the same transactions as mutations. Cleanup clears the prefix range if `preserveData` is false.

## Dependencies and integration points
Depends on bulk setup, RYW transactions, snapshot reads, key encoding helpers, Zipf distribution support, CRC32C, Flow timing, and tester perf metrics.

## Risks and test signals
Risks include complex operation-spec parsing, checksum coverage gaps when row counts do not divide evenly, generated insert keys outside checksum index space, possible bug from bitwise `|` in checksum mutation condition, and very high default TPS. Signals are operation/transaction/conflict/retry metrics, latency sketches, periodic traces, and checksum verification failures or missing checksum keys.
