# sources/storage-engines/foundationdb/fdbserver/coordinator/Coordination.cpp

## Purpose
Implements the coordinator server runtime: a durable generation register, the leader-election register service, forwarding after coordinator changes, and cluster-key rewrites for existing coordinator stores. It is the server-side counterpart to the coordination interfaces used by clients, cluster controllers, and quorum-change code.

## Important APIs, Types, and Functions
- `coordinationServer(dataFolder, ccr)` creates well-known `LeaderElectionRegInterface` and `GenerationRegInterface` endpoints, opens an `OnDemandStore`, and races generation-register serving, leader-register serving, and store errors.
- `LocalGenerationReg` serves `GenerationRegReadRequest` and `GenerationRegWriteRequest` against the local store. Stored values are `GenerationRegVal { readGen, writeGen, val }`.
- `LeaderRegister` is an in-memory actor for one cluster key. It tracks candidates, leaders, waiting notifications, connected clients, and monitored leader DB info.
- `LeaderRegisterCollection` multiplexes per-key `LeaderRegister` instances and persists forwarding records under `fwdKeys` and `fwdTimeKeys`.
- `LeaderServer` validates cluster descriptors, checks forwarding state, and routes leader/open-database requests to the appropriate register.
- `coordChangeClusterKey()` and `changeClusterDescription()` rewrite persisted coordinator data when a cluster key changes.

## Control Flow
Generation reads and writes are serialized by `FlowLock`, read the current encoded `GenerationRegVal`, update read or write generation when allowed, commit the store, and reply. The read path advances `readGen` for the caller generation; the write path succeeds only if no later read or write generation blocks it.

Leader requests first go through `LeaderServer`, which checks persisted forwarding and optional cross-cluster descriptor matching. A key-specific `LeaderRegister` then collects candidacy and heartbeat reports over polling intervals, chooses the best candidate or current leader, sends notifications, and retires itself when no state and no connected clients remain. Open-database and election-result requests may lazily start monitor-leader work and keep long-polling clients attached.

Forwarding requests are durably written before being forwarded into the in-memory register. This ensures restarted coordinators can return the new connection string to clients with stale cluster files.

## State and Persistence Behavior
Persistent state lives in the coordinator `OnDemandStore` under unprefixed generation-register keys and reserved forwarding ranges. `GenerationRegVal` serialization is versioned and explicitly tied to `ProtocolVersion::GenerationRegVal`. Forwarding state stores connection strings and the timestamp when forwarding was set. Cluster-key rewrite logic scans all coordinator key/value entries, renames forwarding keys, updates forwarding values, and updates movable coordinated-state connection strings inside generation-register values.

`coordinationServer` has a simulation-only repair path for inconsistent disk queue creation: if one coordinator disk-queue file is missing after a crash, it deletes the remaining peer file so a later boot can recreate a consistent pair.

## Dependencies and Integration Points
This file depends on `OnDemandStore`, `CoordinationInterface`, `MonitorLeader`, `WorkerInterface.actor`, Flow actors, `ProtocolVersion`, and server knobs. It integrates with `CoordinatedState` through generation-register semantics, `LeaderElection.actor.cpp` through leader election and forwarding RPCs, and cluster-file persistence through `IClusterConnectionRecord`.

## Risks and Edge Cases
Generation-register access is intentionally serialized, so store latency directly affects coordination latency. The leader register has several long-polling queues and guards against unbounded notifications with `MAX_NOTIFICATIONS`. Descriptor mismatch behavior depends on `ENABLE_CROSS_CLUSTER_SUPPORT`; changing that knob affects whether requests for other cluster keys are rejected. Forwarding records can become old, and old-cluster-file use is logged after `FORWARD_REQUEST_TOO_OLD`. The cluster-key rewrite path parses stored values as `GenerationRegVal` in the fallback branch, so only expected coordinator-store layouts should be present there.

## Test Signals
The file includes `/fdbserver/Coordination/localGenerationReg/simple`, validating empty reads, successful writes, read/write generation propagation, and actor liveness. Additional coverage should come from simulation tests that exercise leader election, coordinator forwarding, quorum changes, and the disk-queue recovery path.
