## sources/storage-engines/foundationdb/fdbserver/workloads/ReadAfterWrite.cpp

`ReadAfterWriteWorkload` measures storage propagation delay: the extra time for a committed version to become readable from storage compared with reading an already-established read version. It is a `KVWorkload`, so it uses the common random keyspace helpers without mutating logical state.

Important APIs are `KVWorkload::getRandomKey`, `Transaction::getReadVersion`, `Transaction::setVersion`, `commit`, `DDSketch`, and `error_code_future_version`. The helper `latencyOfRead` retries `future_version` until the storage server can serve the requested version, but rethrows other errors.

Each benchmark iteration chooses a random key, gets a read version in `writeTr`, reads the key to ensure the read version is present on a storage server, writes back the same value or clears the absent key, and commits. It then reads the same key concurrently at the original read version and at the commit version, subtracts baseline read latency from after-write latency, clamps at zero, and records the propagation sample.

State persistence is intentionally neutral: committing the same value or clear should not change user-visible contents, allowing pairing with other workloads. Risks include the write transaction still creating conflict/commit work, repeated `future_version` retry spinning without delay, and metrics depending on the baseline and after-write reads being comparable. The `benchmark` future is not awaited directly; `start` keeps it alive by local future until `delay(testDuration)` returns and cancellation occurs.

Integration points are storage read-version availability, log-to-storage propagation, and KV workload key generation. Test signals are latency metrics: mean, median, 90%, 99%, and max propagation latency. `check` returns true.
