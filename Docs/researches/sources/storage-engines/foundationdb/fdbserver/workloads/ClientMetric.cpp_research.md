# sources/storage-engines/foundationdb/fdbserver/workloads/ClientMetric.cpp

## Purpose
`ClientMetric.cpp` defines `ClientMetric`, a workload that verifies client latency metric entries are generated and advance over time. It can set global client profiling parameters, write random keys to trigger metrics, read the client latency special/system key range, and assert that the latest versionstamp increases after additional writes.

## Important APIs, Types, And Functions
The workload uses `GlobalConfig::prefixedKey`, `fdbClientInfoTxnSampleRate`, `fdbClientInfoTxnSizeLimit`, `runRYWTransaction`, `Tuple`, `ReadYourWritesTransaction`, `Transaction`, and system-key transaction options. Helpers include `getVersionStamp`, `changeProfilingParameters`, `latencyRangeQuery`, `writeRandomKeys`, `writeKeysAndGetLatencyVersion`, and `runner`.

## Control Flow
If `toSet` is true, client 0 writes sampling probability and transaction info size limit in `setup`. `start` on client 0 runs `runner` with a timeout. `runner` writes an initial batch of random keys, waits/queries for the newest client latency entry, parses its versionstamp, writes another batch, and asserts the second newest versionstamp is larger. `latencyRangeQuery` waits for `CSI_STATUS_DELAY`, reads the global config cached values for diagnostic output, and repeatedly scans the latency range until at least one entry is present.

## State And Persistence
The workload persists random user keys, global configuration values for client profiling when enabled, and observes generated client latency info under `\xff\x02/fdbClientInfo/client_latency/...`. It does not delete the random keys or latency entries.

## Dependencies And Integration Points
It depends on the client status info pipeline, global configuration propagation, system key access, versionstamp key layout, and transaction sampling. The versionstamp offsets are derived from a sample key string and must match the client latency key format.

## Risks
The workload can wait indefinitely in `latencyRangeQuery` until the outer timeout fires if metrics are not produced, for example when sampling probability is too low or profiling is disabled. The `writeRandomKeys` loop checks `cnt >= total` before incrementing, causing one extra write relative to the intuitive total. `runner` catches errors and only logs them, so some failures may not affect `check`, which always returns true.

## Test Signals
Trace/output signals include `WaitingForLatencyMetricToBePresent`, `WriteKeysAndGetLatencyVersionFailed`, `ClientMetricErrorWhenWriteKeys`, and `ClientMetricError`. The strongest assertion is `vs2 > vs1`, indicating newer latency metrics were added.
