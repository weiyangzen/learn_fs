# sources/storage-engines/foundationdb/fdbserver/workloads/IndexScan.cpp

## Purpose
Range-read performance workload that repeatedly scans an index key range in bounded byte chunks and reports row/chunk/failure metrics.

## Important APIs, types, and functions
`IndexScanWorkload` derives from `KVWorkload`, using inherited `keyForIndex`, `allKeys`, and `nodeCount` helpers. It exposes `bytesPerRead`, `transactionDuration`, `singleProcess`, and `readYourWrites`, and tracks rows, chunks, scans, failed transactions, and total fetch time.

## Control flow
The start phase optionally limits execution to client 0, warms the location cache for `allKeys`, waits briefly, and runs `serialScans` for `testDuration`. Each `scanDatabase` starts at a random index in the first half of the database, reads until the end key using `GetRangeLimits(ROW_LIMIT_UNLIMITED, bytesPerRead)`, advances by `firstGreaterThan(last.key)`, and breaks a transaction after empty result, no `more`, or `transactionDuration`.

## State and persistence behavior
The workload does not set up or write data; comments state that data is prepared externally. It only accumulates in-memory metrics.

## Dependencies and integration points
Depends on `KVWorkload` key generation, `ReadYourWritesTransaction`, optional `READ_YOUR_WRITES_DISABLE`, location-cache warming, and standard range read retry behavior.

## Risks and test signals
`check` always returns true, so this is a measurement workload. Risks include repeated scans over missing externally populated data, byte-limit sensitivity, and false failure count inflation except for actor cancellation. Signals are metrics for failed transactions, rows, scans, chunks, elapsed fetch time, rows/sec, and rows/chunk.
