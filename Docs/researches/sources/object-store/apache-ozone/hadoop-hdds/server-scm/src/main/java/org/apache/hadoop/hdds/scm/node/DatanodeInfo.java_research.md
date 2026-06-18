# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/node/DatanodeInfo.java

Purpose: `DatanodeInfo` extends `DatanodeDetails` with SCM runtime metadata: last heartbeat, storage reports, metadata-volume reports, node status, command counts, layout versions, failed-volume counts, and pending container allocation tracking.

Important APIs and types: Important methods include `updateLastHeartbeatTime`, `updateLastKnownLayoutVersion`, `updateStorageReports`, `updateMetaDataStorageReports`, `getNodeStatus`, `setNodeStatus`, `setCommandCounts`, `getCommandCount`, and `getPendingContainerAllocations`. It uses `ReadWriteLock`, `LayoutVersionProto`, `StorageReportProto`, `MetadataStorageReportProto`, `CommandQueueReportProto`, and `PendingContainerTracker.TwoWindowBucket`.

Control flow: Construction copies base datanode details, initializes heartbeat time, normalizes layout versions, creates empty reports and command maps, and creates a per-node pending-container bucket. Report update methods compute derived counters and replace snapshots under the write lock. `setCommandCounts` clears the previous heartbeat command counts, reads each command/count pair from the datanode report, normalizes negative values to zero, adds any SCM-side commands that will be sent in the current heartbeat, and preserves entries not reported by the datanode.

State and persistence behavior: This is volatile SCM memory. The only persistent input is the datanode's own details and persisted operational state copied into `NodeStatus` elsewhere. Storage and command snapshots are replaced on heartbeat reports; pending allocations age through a two-window bucket.

Dependencies and integration points: `NodeStateManager` creates and updates `DatanodeInfo`; `SCMNodeManager` uses it for heartbeat processing, storage accounting, command queue visibility, placement decisions, and MXBean reporting. Upgrade logic uses the last known layout version to move nodes between `HEALTHY` and `HEALTHY_READONLY`.

Risks: The class warns that lost updates are possible if callers read, mutate, and write `NodeStatus` without higher-level coordination. Report lists are stored by reference, so callers should avoid mutating lists after update. `lastStatsUpdatedTime` is not read under lock. Unknown command types are skipped, which can mask version skew while keeping SCM running.

Test signals: Tests should cover lock-safe heartbeat updates, storage failed-volume counts, metadata volume counts, layout version update ignoring nulls, command count replacement/merge semantics, unknown and negative command report handling, pending bucket rolling, and equality inherited from `DatanodeDetails`.
