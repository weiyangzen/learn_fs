# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthMonitor.h

## Purpose

`ClusterHealthMonitor.h` defines the cluster-health level model, event-provider abstraction, production provider, and monitor API.

## Important APIs, Types, and Functions

- `Level` defines `OUTAGE`, `CRITICAL_INTERVENTION_REQUIRED`, `INTERVENTION_REQUIRED`, `SELF_HEALING`, `METRICS_MISSING`, and `HEALTHY`.
- `LatestWorkerEvents` is optional `(WorkerEvents, failed-address set)` data.
- `IWorkerEventProvider` abstracts recovery state, one-replica policy, and latest event-log access by role/scope.
- `WorkerEventProvider` stores production snapshots of workers and role interfaces.
- `Monitor` owns factors and a provider; `create()` wires defaults and `run()` emits metrics.

## Control Flow

The header defines a pull contract: factors ask a provider for the signal they need, while production code and tests can supply different providers.

## State and Persistence Behavior

All provider state is in-memory. Interfaces are copied snapshots from the controller; no durable state is managed here.

## Dependencies and Integration Points

The header depends on factor declarations, storage/TLog interfaces, `RecoveryState`, `WorkerEvents`, and Flow. It is the boundary between controller state and health evaluation.

## Risks

Consumers rely on the difference between absent data, empty successful data, and failed event-log requests. Collapsing those cases can produce incorrect `HEALTHY` or `METRICS_MISSING` results.

## Test Signals

The fake provider in `ClusterHealthMonitorTesting.cpp` implements this interface and validates factor behavior across present, missing, empty, and partially failed events.
