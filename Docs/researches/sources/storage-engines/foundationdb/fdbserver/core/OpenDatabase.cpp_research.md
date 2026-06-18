# sources/storage-engines/foundationdb/fdbserver/core/OpenDatabase.cpp

## Purpose
`OpenDatabase.cpp` builds a client `DatabaseContext` from server-side `ServerDBInfo`. It is the bridge used by server actors that need to issue ordinary client-style transactions while tracking cluster interface changes.

## Important APIs, types, and functions
- `extractClientInfo` watches `AsyncVar<ServerDBInfo>` and publishes a shrunk `ClientDBInfo` into another `AsyncVar`.
- `openDBOnServer` creates a `DatabaseContext` with task priority, lock-awareness, and optional locality load balancing, then initializes global config triggers.

## Control flow
`extractClientInfo` loops forever: copy `db->get().client`, call `shrinkProxyList` with cached commit and GRV proxy lists, publish with `setUnconditional`, and wait on `db->onChange()`. `openDBOnServer` allocates the target `AsyncVar<ClientDBInfo>`, starts `extractClientInfo` as the database context maintenance future, supplies local locality only when locality load balancing is enabled, and registers actor-lineage profiler global-config triggers.

## State and persistence behavior
There is no direct persistence. State is in async variables and the created `DatabaseContext`. `shrinkProxyList` preserves stable proxy interface objects across updates where possible to reduce churn.

## Dependencies and integration points
The code depends on `DatabaseContext`, `MonitorLeader` proxy helpers, `GlobalConfig`, `ActorLineageProfiler`, and `WorkerInterface.actor.h` server DB structures. Server subsystems use `openDBOnServer` to get a `Database` backed by the same cluster metadata they already observe.

## Risks and edge cases
If `ServerDBInfo` changes rapidly, `extractClientInfo` publishes every change without backpressure. Misconfigured locality load balancing can cause the created context to omit locality data. Global config is initialized from the current client info pointer and the source `AsyncVar`, so lifetime and mutation assumptions are tied to `ServerDBInfo`.

## Test signals
There are no local tests. Integration behavior is visible through client transaction success from server processes and profiler config effects for `samplingFrequency`, `samplingProfilerUpdateFrequency`, `samplingWindow`, and `samplingProfilerUpdateWindow`.
