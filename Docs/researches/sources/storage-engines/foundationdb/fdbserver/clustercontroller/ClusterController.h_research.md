# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterController.h

## Purpose

`ClusterController.h` is the central in-memory control surface for FoundationDB cluster-controller behavior. It defines worker registration state, database metadata publication state, recruitment helpers for transaction-system roles, worker health aggregation, remote-DC failover decisions, and the hook points for the cluster-health metric monitor. Although this is a header, it contains substantial inline actor/control logic used by the cluster controller implementation.

## Important APIs, Types, and Functions

- `WorkerInfo` owns a registered process's watcher, registration reply promise, generation, reboot count, initial/current process classes, priority information, `WorkerDetails`, role halt futures, and reported issues.
- `WorkerFitnessInfo` and `RoleFitness` encode recruitment quality: process-class fitness, process reuse count, selected worker count, and TLog-specific degraded-process penalties.
- `ClusterControllerData::DBInfo` tracks published client/server DB info, recovery flags, configuration, client status, recovery data, and client-count pruning.
- `UpdateWorkerList` batches worker-list KV updates under `workerListKeys`.
- Recruitment helpers select storage, seed, TLog, satellite-log, proxy, resolver, backup, master, cluster-controller, and remote-DC workers.
- Health/failover helpers update peer health, derive degraded/disconnected servers, decide recovery/failover, and track recent health-triggered recoveries.
- `updateClusterHealthMonitorInputs()` bridges controller state into `cluster_health::WorkerEventProvider`.

## Control Flow

Workers register into `id_worker`; `workerAvailable()` combines startup grace, failure-monitor availability, and reboot-stability checks. Recruitment filters by role fitness, locality, exclusions, degraded status, low-disk issue flags, process reuse, and controller-DC preference. TLogs use optimized simple/complex policy paths with a backup policy-engine path. Multi-region recruitment can swap preferred regions based on priority, controller DC, version lag, and remote health, then updates `desiredDcIds`.

Worker health flows from `UpdateWorkerHealthRequest` into `workerHealth`, through expiration cleanup in `updateRecoveredWorkers()`, and into `getDegradationInfo()`, which deterministically selects likely bad endpoints and optional whole-satellite degradation. Recovery and failover decisions then check topology, recovery state, controller exclusion, bounded exclusion count, remote health, and version-lag safety.

## State and Persistence Behavior

Most state is volatile controller memory: worker maps, role recruitment requests, health reports, degraded-server exclusions, role recruitment `AsyncVar`s, failover priority variables, and monitor inputs. Persistent effects are limited to worker-list KV updates and the published `AsyncVar<ClientDBInfo>`/`AsyncVar<ServerDBInfo>` surfaces. Client status is pruned periodically based on coordinator register timing.

## Dependencies and Integration Points

The header integrates with FDB database context, worker/storage/TLog interfaces, replication policies, locality, process classes, failure monitoring, `RatekeeperMonitor`, Flow actors/futures, server knobs, and `ClusterHealthMonitor`. It exposes `clusterRegisterMaster()` and stores the cluster-health provider/monitor for metric emission.

## Risks

Recruitment is sensitive to fitness ordering, reuse counters, degraded status, and locality constraints. Small changes can cause nondeterminism, worse placement, or recovery churn. Health failover thresholds are knob-heavy and can be too aggressive or too conservative. Worker issues are stringly typed, so producer/consumer drift can silently change recruitment behavior.

## Test Signals

Simulation-only assertions compare optimized and backup recruitment and detect nondeterministic fitness. Operational traces include `RecruitStorageTry`, `GetTLogTeamWorkerUnavailable`, `BetterMasterExists`, `NewRecruitmentIsWorse`, `ClusterControllerUpdateWorkerHealth`, and `ClusterControllerTriggerFailover`.
