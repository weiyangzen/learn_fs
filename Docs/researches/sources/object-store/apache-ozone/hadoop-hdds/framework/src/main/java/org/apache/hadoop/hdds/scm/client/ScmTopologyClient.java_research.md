# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/scm/client/ScmTopologyClient.java

## Purpose

`ScmTopologyClient` keeps an OM-side cached network topology refreshed from SCM in a background thread.

## Important APIs, Types, and Functions

`start(ConfigurationSource)` fetches initial topology and schedules polling. `getClusterMap()` returns the cached `NetworkTopology`. `stop()` shuts down the executor. `parseRefreshDuration` reads `ozone.om.network.topology.refresh.duration`.

## Control Flow

Startup fetches `InnerNode` from `ScmBlockLocationProtocol`, wraps it in `NetworkTopologyImpl` using the configured schema file, stores it in an `AtomicReference`, and schedules fixed-rate `checkAndRefresh`. Refresh compares the root `InnerNode`; if changed, it rebuilds and swaps the topology.

## State and Persistence Behavior

State is an in-memory atomic cache and scheduled executor. There is no persistence.

## Dependencies and Integration Points

It depends on SCM block-location protocol, `NetworkTopologyImpl`, `InnerNode`, and OM/SCM network topology config keys.

## Risks and Test Signals

`checkAndRefresh` throws `UncheckedIOException` inside a scheduled task, which can stop future executions depending on executor behavior. `getClusterMap()` fails before `start()`. Tests should cover initial load, unchanged/changed refresh, stop behavior, parse duration, and fetch failures.
