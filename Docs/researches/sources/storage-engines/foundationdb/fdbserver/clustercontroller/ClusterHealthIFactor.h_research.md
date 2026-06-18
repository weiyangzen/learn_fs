# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterHealthIFactor.h

## Purpose

`ClusterHealthIFactor.h` defines the factor interface and declares the built-in factors used by the cluster-health monitor.

## Important APIs, Types, and Functions

- `IFactor` exposes `getName()` and asynchronous `fetchLevel()`.
- `TrackCodeProbes` controls branch probe emission.
- `StorageSpaceFactor`, `TLogSpaceFactor`, and `RkThrottlingFactor` hold constructor-provided thresholds.
- `StorageReplicationFactor`, `RecoveryStateFactor`, and `ProcessErrorsFactor` are threshold-free signal checks.

## Control Flow

The monitor owns a vector of `IFactor` implementations and calls each factor against a provider. The interface keeps evaluation independent from production event-log collection.

## State and Persistence Behavior

The header only defines in-memory objects and threshold fields. No persistent state is represented.

## Dependencies and Integration Points

It forward-references `Level` and `IWorkerEventProvider`, uses Flow `Future`, and is consumed by both monitor implementation and tests.

## Risks

Factor names become trace-detail suffixes, so renames can break dashboards. New factors require declaration, implementation, monitor wiring, and test coverage.

## Test Signals

All declared concrete factors are directly exercised by fake-provider tests in `ClusterHealthMonitorTesting.cpp`.
