# sources/storage-engines/foundationdb/fdbserver/workloads/Inventory.cpp

## Purpose
Transactional inventory counter workload that mixes point reads with multi-product read-modify-write increments and verifies final counts are within in-memory expected bounds.

## Important APIs, types, and functions
`InventoryTestWorkload` derives from `TestWorkload` and tracks per-key `minExpectedResults` and `maxExpectedResults`, actor and product counts, rates, clients, and counters. Key methods are `chooseProduct`, `inventoryTestWrite`, `inventoryTestClient`, `inventoryTestCheck`, `failures`, and metrics reporting.

## Control flow
Only client 0 runs actors. Each actor is Poisson-paced and randomly chooses write or read. Write transactions choose a set of products, pessimistically increment max bounds, read each product's current count, set count+1, retry on errors while adjusting max bounds, then increment min bounds after commit. Read transactions only read a random product with retry. Check reads the full product key range and compares actual counts to expected min/max bounds.

## State and persistence behavior
Database state is plain decimal count strings under `doubleToTestKey(product/nProducts)`. In-memory bounds account for transactions that may have been cancelled, retried, or committed. No cleanup occurs.

## Dependencies and integration points
Uses FoundationDB transactions, deterministic random key generation, tester Poisson pacing, and trace/perf metric utilities.

## Risks and test signals
The workload is single-client despite a multi-client note, and expected-bound bookkeeping is subtle around actor cancellation and retries. Count parsing uses `atoi` and assumes nonnegative bounded counts. Signals are client future errors, final actual count outside min/max, and latency/throughput perf metrics.
