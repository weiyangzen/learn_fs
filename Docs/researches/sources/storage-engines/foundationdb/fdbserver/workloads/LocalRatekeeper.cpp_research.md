# sources/storage-engines/foundationdb/fdbserver/workloads/LocalRatekeeper.cpp

## Purpose
Simulation workload that validates storage-server local ratekeeper behavior when durability lag rises. It checks both reported `localRateLimit` and whether reads to a lagging storage server are rejected as future versions.

## Important APIs, types, and functions
The file-local `getRandomStorage` reads `serverListKeys` and decodes a `StorageServerInterface`. `LocalRatekeeperWorkload` exposes `startAfter`, `blockWritesFor`, `testFailed`, `testStorage`, and `_start`. It uses `StorageQueuingMetricsRequest`, `GetValueRequest`, `SERVER_KNOBS->STORAGE_DURABILITY_LAG_SOFT_MAX/HARD_MAX`, and simulator `disableFor`.

## Control flow
Client 0 in simulation waits `startAfter`, picks a random storage server, disables its `updateStorage` actor for `blockWritesFor`, waits roughly until soft lag should be reached, then races `testStorage` with the block duration. `testStorage` repeatedly fetches queuing metrics, computes the expected local rate limit linearly from durability lag, sends 100 direct `getValue` requests at a current read version, and counts `future_version` rejections.

## State and persistence behavior
No user data is written. Runtime state is the disabled simulator role and `testFailed`. System key reads require `ACCESS_SYSTEM_KEYS`.

## Dependencies and integration points
Integrates with storage server interfaces, local ratekeeper metrics, simulator role disabling, transaction read versions, and direct storage-server read requests.

## Risks and test signals
Risks are timing sensitivity around lag accumulation, selecting a storage server whose state changes, and treating any direct request error as workload failure. Signals are `StorageRateLimitTooFarOff`, `LoadBalancedResponseReturnedError`, `RejectedVersions` traces, and `check` returning `!testFailed`.
