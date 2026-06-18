# sources/storage-engines/foundationdb/fdbserver/workloads/Throttling.cpp

## Purpose
`ThrottlingWorkload` runs a random read-write workload whose transaction start rate is controlled by health-metrics TPS limits. It also validates special-key health metrics JSON schemas for aggregate, storage, and log metrics.

## Important APIs, Types, and Functions
The file defines `TokenBucket` and `ThrottlingWorkload : KVWorkload`. It uses `ReadYourWritesTransaction`, special key range `\xff\xff/metrics/health/`, `JSONSchemas::aggregateHealthSchema`, `storageHealthSchema`, `logHealthSchema`, `schemaMatch()`, `readJSONStrictly()`, `UID::fromString()`, and `PerfMetric`.

## Control Flow
`TokenBucket::tokenAdder()` periodically adds tokens according to `transactionRate`; `startTransaction()` waits until a token is available. `clientActor()` loops forever: wait for a token, reset a transaction, perform configured random reads and writes, commit, and count successes while ignoring transaction errors. `specialKeysActor()` repeatedly reads health metrics, validates key prefixes and JSON schemas, updates `tokenBucket.transactionRate` from aggregate `tps_limit * throttlingMultiplier / clientCount`, and sleeps with jitter. `start()` runs all actors and the token adder under `testDuration`.

## State and Persistence Behavior
Database state is random keys and values under `KVWorkload` normal keyspace. Special-key reads observe cluster health state but do not persist data. Runtime state is token bucket size/rate and `correctSpecialKeys`.

## Dependencies and Integration Points
The workload integrates with management health special keys, JSON schema definitions, RYW transactions, KVWorkload random key generation, server/client knobs, and Flow tracing/code probes.

## Risks and Edge Cases
Client transactions ignore all non-cancellation errors, so write workload failures do not fail the test. The correctness gate is schema validation only. Special-key actor calls `tr.onError(err)` after errors but does not always reset transaction explicitly on successful iterations, relying on RYW behavior. `TokenBucket` starts with `transactionRate = 0`, so client actors may block until health metrics are read.

## Test Signals
`check()` returns `correctSpecialKeys`. Errors include `AggregateHealthSchemaValidationFailed`, `StorageHealthSchemaValidationFailed`, and `LogHealthSchemaValidationFailed`. Metrics report `TransactionsCommitted`.
