# sources/storage-engines/foundationdb/fdbserver/workloads/GetEstimatedRangeSize.cpp

Purpose: Implements a focused workload that verifies `getEstimatedRangeSizeBytes(normalKeys)` returns a plausible estimate after optional bulk setup.

Important APIs/types/functions: `GetEstimatedRangeSizeWorkload`, `bulkSetup`, `checkSize`, `sizeIsAsExpected`, `getSize`, `ReadYourWritesTransaction::getEstimatedRangeSizeBytes`, `doubleToTestKey`, and `normalKeys`.

Control flow: Setup bulk-loads `nodeCount` deterministic keys unless `checkOnly` is true. Client 0 start calls `checkSize`, which repeatedly calls `getSize`. `getSize` reads the estimated normal-key range size, traces it, and if outside the broad expected window waits five seconds and retries for up to 300 seconds before returning the last estimate. `checkSize` asserts the estimate is within range.

State and persistence behavior: Persistent state is the optional bulk-loaded cycle-style key/value set under `keyPrefix`. Runtime state is limited to retry delay accumulation.

Dependencies/integration: Uses `BulkSetup.h`, Native API range-size estimation, client knobs, deterministic key/value encoding, simulator tracing, and workload client gating.

Risks: The expected window is intentionally wide because the API is approximate. If `checkOnly` is used without preloaded data, the assertion will fail. Estimation may lag data distribution/storage metrics enough to consume the full 300 second retry window.

Test signals: `GetSizeResult`, `GetSizeError`, and the final `ASSERT(sizeIsAsExpected(size))`.
