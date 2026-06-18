# sources/storage-engines/foundationdb/fdbserver/workloads/DDMetricsExclude.cpp

Purpose: Defines `DDMetricsExclude`, which excludes a configured storage-server address and measures moving-data volume and duration until data distribution drains the exclusion.

Important APIs/types/functions: `DDMetricsExcludeWorkload`, `excludeServers`, `StatusClient::statusFetcher`, `StatusObjectReader`, `getMovingDataAmount`, `AddressExclusion`, and metrics for peak moving data, queue bytes, in-flight bytes, duration, and throughput.

Control flow: `start` builds an exclusion from `excludeIp` and `excludePort`, calls `excludeServers`, then polls status every 2.5 seconds. It reads `cluster.data.moving_data.in_queue_bytes` and `in_flight_bytes`, updates peaks, and completes when the sum is exactly zero. `check` computes `movingDataPerSec`.

State and persistence behavior: Persistent cluster state is changed through the management exclusion keys. Runtime state records peak byte counts and completion time. There is no explicit include/cleanup in this workload.

Dependencies/integration: It integrates Management API exclusions, status JSON schema, data distribution movement accounting, and tester metrics.

Risks: The hard-coded default address may not exist in many simulations. If `ddDone` remains zero, `movingDataPerSec = peakMovingData / ddDone` risks invalid numeric output. Status schema changes or absent moving-data fields return `-1.0`, which can affect peak logic and liveness.

Test signals: `DDMetricsExcludeCheck`, `DDMetricsExcludeError`, and the five exported moving-data metrics.
