# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/SCMNodeManager.java

## Purpose
`SCMNodeManager` is the Storage Container Manager side implementation of `NodeManager`. It owns datanode registration, heartbeat command dispatch, node reports, node operational state synchronization, topology registration, storage and usage summaries, pipeline/container membership delegation, and JMX/metrics-facing views of the cluster. It coordinates the lower-level `NodeStateManager`, in-memory command queues, `PendingContainerTracker`, SCM layout-version finalization, and event publication.

## Important APIs, Types, And Functions
The constructor wires `NodeStateManager`, `CommandQueue`, `SCMNodeMetrics`, `PendingContainerTracker`, `NetworkTopology`, SCM HA context, layout version manager, configuration-derived pipeline/container limits, and non-writable-node filtering. `register` validates datanode software layout version, resolves current RPC address, inserts or updates the datanode in the topology and state manager, updates hostname/IP reverse indexes, processes the initial node report, and emits `NEW_NODE` or `NODE_ADDRESS_UPDATE`.

Heartbeat handling is centered on `processHeartbeat`, which updates last heartbeat, metrics, operational-state reconciliation, drains queued commands, invokes optional send-command callbacks, and folds datanode command queue reports into `DatanodeInfo`. Layout and finalization handling flows through `processLayoutVersionReport` and `sendFinalizeToDatanodeIfNeeded`, with leader-only `FinalizeNewLayoutVersionCommand` publication. Query APIs expose node counts, status, all nodes, storage stats, usage info, peer lists, pipeline/container memberships, command counts, and last heartbeat.

Operational-state APIs include `setNodeOperationalState`, `updateDatanodeOpState`, `opStateDiffers`, and `maybeNotifyReplicationManager`. Storage aggregation APIs include `getStats`, `getNodeStats`, `getNodeStat`, `getNodeInfo`, `getNodeStatusInfo`, `getNodeStatistics`, `calculateStorageCapacity`, `calculateStoragePercentage`, `getTotalReserved`, and `getTotalFilesystemUsage`. Pipeline/container integration passes through `addPipeline`, `removePipeline`, `getPipelines`, `addContainer`, `removeContainer`, and `getContainers`.

## Control Flow
Registration first rejects incompatible datanode software layout versions. It updates IP/hostname from `Server.getRemoteIp` when inside RPC, computes network identity/location, and either adds a new node or refreshes an existing node if address or version changed. New nodes are inserted into `NetworkTopology` before `NodeStateManager`, then the code verifies that topology parent assignment is present. Existing-node address changes update the DNS-to-datanode map, topology, state manager, report data, and fire the address-update event.

Heartbeats update liveness before acquiring the manager write lock for command queue mutation. Leader SCMs treat SCM node state as authoritative: if a heartbeat reports a different persisted operational state, SCM queues `SetNodeOperationalStateCommand` with the leader term. Followers instead update their local view from the heartbeat. After that, the stored `DatanodeDetails` persisted operational fields are refreshed and replication manager is notified on relevant transitions.

JMX and metrics flows build snapshots, not linearizable views. Node counts are grouped by operational and health state; storage summaries skip dead in-service nodes for usage-state aggregation and withhold raw filesystem totals if any live report lacks filesystem fields. Non-writable nodes are detected by health/operational writability plus Ratis volume/container space checks. Removal requires a node to be decommissioned or dead, removes it from topology and node maps, clears reverse address indexes, and drains pending commands.

## State And Persistence Behavior
Most state here is in-memory and delegated. `NodeStateManager` owns node lifecycle state; `CommandQueue` owns per-datanode commands; `dnsToDnIdMap` maps host/IP strings to one or more `DatanodeID`s; `PendingContainerTracker` tracks optimistic container allocation reservations. `SCMNodeManager` also registers an MBean and a Hadoop metrics source that must be unregistered on close.

Persistent behavior is indirect. Node operational state is persisted by datanodes and reconciled via heartbeats; SCM sends update commands when leader state differs. Layout finalization commands cause datanodes to update their metadata layout version. Node and pipeline/container membership changes affect SCM state stores through collaborators such as `NodeStateManager` and `PipelineStateManager`, not direct DB writes in this class.

The class uses a `ReentrantReadWriteLock` around command queue and some removal operations, while `NodeStateManager` and concurrent maps provide their own synchronization. Returned lists and maps are intentionally snapshots and may be stale immediately after creation.

## Dependencies And Integration Points
The class integrates with SCM event bus events including `NEW_NODE`, `NODE_ADDRESS_UPDATE`, `DATANODE_COMMAND`, `DATANODE_COMMAND_COUNT_UPDATED`, and `REPLICATION_MANAGER_NOTIFY`. It depends on `NetworkTopology` for rack placement, `SCMContext` for leader/term/safemode behavior, `HDDSLayoutVersionManager` and `FinalizationManager` for upgrades, protobuf reports from datanodes, `PipelineManager` through the SCM context for peer calculation, and Hadoop metrics/JMX.

It is consumed by datanode RPC handlers, pipeline placement, replication manager, container manager, admin/decommission flows, dashboards, and metrics scrapers. `NonWritableNodeFilter` shares placement semantics by using `SCMCommonPlacementPolicy.hasEnoughSpace` plus committed-space fallback.

## Risks And Edge Cases
The registration path has several race-sensitive side effects: topology, state map, DNS reverse index, and node reports must remain consistent when IP/hostname changes. If `getNodesByAddress` maps a removed ID to `null`, callers must tolerate nullable entries because it maps through `getNode`. `calculateStoragePercentage` divides by capacity without a zero-capacity guard, so bad reports can produce invalid percentages.

Snapshot methods should not be used for strict invariants. Nested read locks call other methods that acquire the same read lock, which is safe with `ReentrantReadWriteLock` but should be considered when changing locking. `removeNode` calls `getCommandQueue` while already holding the write lock; this relies on reentrant write locks. Leader-only command publication must handle `NotLeaderException` because leadership can change between checks and term retrieval.

## Test Signals
High-value tests include registration of new and existing nodes, address/hostname update and DNS index cleanup, topology parent assignment, heartbeat command drain and command-count report merging, leader-vs-follower operational-state reconciliation, layout finalization command emission, node report storage aggregation, non-writable-node metrics, pending allocation rollback, and removal preconditions. Concurrency tests should exercise command queue locking, stale snapshot behavior, and address updates racing with lookups.
