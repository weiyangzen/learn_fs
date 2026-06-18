# sources/storage-engines/foundationdb/fdbserver/core/QuietDatabase.cpp

## Purpose
`QuietDatabase.cpp` implements the simulation/test utility that waits for a cluster to become quiet: no meaningful data movement, bounded log/storage queues, stable DD activity, no non-TSS recruitment, acceptable version offset, and bounded multi-region lag. It also includes helper functions for discovering workers and querying runtime metrics through event-log request interfaces.

## Important APIs, types, and functions
- `getWorkers`, `getMasterWorker`, `getDataDistributorWorker`, `getCoordWorkers`, `getStorageServers`, and `getStorageWorkers` discover cluster actors from `ServerDBInfo` and system keys.
- Metric helpers include `getDataInFlight`, `getTLogQueueInfo`, `getMaxStorageServerQueueSize`, `getDataDistributionQueueSize`, `getTeamCollectionValid`, `getDataDistributionActive`, `getStorageServersRecruiting`, `getVersionOffset`, and `getDatacenterLag`.
- `repairDeadDatacenter` and `reconfigureAfter` are simulation-only helpers for fearless/multi-region tests.
- `enableConsistencyScanInSim` and `disableConsistencyScanInSim` manage consistency scan state around quieting.
- `QuietDatabaseChecker` records failed gates, trace output, and simulation timeout assertions.
- `waitForQuietDatabase` and wrapper `quietDatabase` are the exported quieting flow.

## Control flow
`waitForQuietDatabase` starts with a recovery wait, disables perpetual storage wiggle, disables backup workers, disables consistency scan, and disables DD pipeline control in simulation. It then repeatedly locates the data distributor and concurrently queries data-in-flight, TLog queues, DD queue, team collection validity, storage queue sizes, DD active state, recruitment state, version offset, and datacenter lag. Each loop logs a `QuietDatabase<phase>` event, requires all gates to pass, and needs three consecutive successes before returning. Retryable missing attributes and timeouts are traced and retried; other errors propagate.

## State and persistence behavior
Most reads are non-mutating event-log requests or system-key reads. Mutating side effects are intentional test setup actions: `setPerpetualStorageWiggle(false)`, `disableBackupWorker`, consistency scan config writes through `SystemDBWriteLockedNow`, and simulation reconfiguration with `ManagementAPI::changeConfig` when a datacenter is dead. The file also maintains the process-global `g_ddPipelineControlEnabled` switch.

## Dependencies and integration points
The file integrates with `WorkerInterface` event-log RPCs, `ServerDBInfo`, `ReadYourWritesTransaction`, `RunRYWTransaction`, `ManagementAPI`, simulator state, `FDBSimulationPolicy`, and consistency scan configuration. It is used by simulation workloads and test teardown/checkpoint phases to surface stuck data distribution earlier than generic simulation timeouts.

## Risks and edge cases
Event-log metric names and fields are stringly typed (`TotalDataInFlight`, `TLogMetrics`, `StorageMetrics`, `MovingData`, `TeamCollectionInfo`, etc.); missing or changed fields cause retries or errors. TLog queue inspection is noted as not robust to TLog failure. In simulation, the quiet checker asserts if DD appears stuck past the budget. Multi-region repair is simulation-specific and can change configuration when one datacenter is dead. Team collection validation includes workaround logic for remover oscillation and minimum team counts.

## Test signals
Trace events are the primary signal: `QuietDatabase<phase>Begin/Done/Fail/Retry/Error`, `QuietDatabaseFailure`, `MaxTLogQueueSize`, `MaxStorageServerQueueSize`, `DataDistributionQueueSize`, `GetTeamCollectionValid`, `ConsistencyScan_Sim*`, and `DisablingFearlessConfiguration`. Successful completion requires three consecutive quiet checks.
