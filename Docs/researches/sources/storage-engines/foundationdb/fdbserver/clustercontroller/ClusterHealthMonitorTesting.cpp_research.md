# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthMonitorTesting.cpp

## Purpose

`ClusterHealthMonitorTesting.cpp` provides Flow unit tests for every concrete cluster-health factor with deterministic fake provider input.

## Important APIs, Types, and Functions

- `FakeWorkerEventProvider` implements `IWorkerEventProvider` with per-scope maps keyed by event name.
- Helpers build space metrics, process-error metrics, ratekeeper updates, and latest-worker-event wrappers.
- `MovingDataMetricsBuilder` builds data-distributor replication counters with defaults.
- Test cases cover storage space, TLog space, storage replication, recovery state, process errors, and ratekeeper throttling.

## Control Flow

Each test configures the fake provider, awaits one factor's `fetchLevel()`, and asserts the expected `Level`. Role-specific stale-event tests ensure factors query the intended provider method.

## State and Persistence Behavior

All data is in-memory test state using synthetic `NetworkAddress` values. There is no persistence.

## Dependencies and Integration Points

The tests use Flow `UnitTest`, `RecoveryState`, `ClusterHealthIFactor.h`, and `ClusterHealthMonitor.h`, validating the factor/provider contract.

## Risks

Tests focus on factor mapping and do not cover production RPC timeout behavior, monitor aggregation scheduling, or every malformed-field path.

## Test Signals

Covered branches include healthy/intervention/critical thresholds, missing metrics, role filtering, zero-replica outage, one-replica criticality, repair self-healing, recovery outage/self-healing/healthy mapping, process-error handling, partial failures, zero TPS-limit outage, and idle ratekeeper healthy behavior.
