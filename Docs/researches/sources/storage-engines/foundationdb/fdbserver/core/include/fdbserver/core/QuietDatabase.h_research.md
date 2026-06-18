# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/QuietDatabase.h

## Purpose
This header declares helper actors used by tests and operational workflows to determine whether a database is quiet, inspect queues, get workers/storage servers, and perform simulation-only recovery/reconfiguration actions.

## Important APIs, Types, And Functions
Important functions include `getDataInFlight`, `getTLogQueueInfo`, `getMaxStorageServerQueueSize`, `getDataDistributionQueueSize`, `getTeamCollectionValid`, `getStorageServers`, `getWorkers`, `getMasterWorker`, `repairDeadDatacenter`, `reconfigureAfter`, `getStorageWorkers`, `getCoordWorkers`, `enableConsistencyScanInSim`, `disableConsistencyScanInSim`, `disableDDPipelineControl`, and `isDDPipelineControlEnabled`.

## Control Flow
Callers pass a `Database` and usually an `AsyncVar<ServerDBInfo>`; implementations query system keyspace and role interfaces, then aggregate queue/worker state. Simulation helpers alter consistency-scan or DD-pipeline behavior for test completion.

## State And Persistence Behavior
Most functions read cluster state. `repairDeadDatacenter` and `reconfigureAfter` can mutate configuration state. DD pipeline control is a plain process-local boolean intended for test harnesses.

## Dependencies And Integration Points
It depends on database context, Native API, tester and worker interfaces, storage-server interfaces, and `ServerDBInfo`. It integrates with workload tests, consistency checking, DD quiescence, and database recovery tests.

## Risks And Edge Cases
These helpers can observe changing cluster state and may race recovery or recruitment. Simulation-only switches should not leak into production behavior. Queue estimates depend on role availability and current `ServerDBInfo`.

## Test Signals
Signals include quiet-database waits completing after workloads, accurate queue-size aggregation, correct worker filtering flags, reconfigure-after timing, and successful consistency-scan enable/disable in simulation.
