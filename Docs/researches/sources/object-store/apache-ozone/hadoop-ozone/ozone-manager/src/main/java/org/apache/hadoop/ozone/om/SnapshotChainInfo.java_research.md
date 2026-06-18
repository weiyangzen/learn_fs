# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SnapshotChainInfo.java

Purpose: `SnapshotChainInfo` is the node model for OM's in-memory snapshot chains. Each node stores its own snapshot UUID and links to previous and next snapshot UUIDs.

Important APIs and types: It exposes setters for previous and next IDs, getters for all three UUIDs, boolean `hasNextSnapshotId` and `hasPreviousSnapshotId`, plus `equals` and `hashCode`.

Control flow: There is no complex control flow; `SnapshotChainManager` mutates these nodes when adding or deleting snapshots from global and path-specific linked lists.

State and persistence behavior: State is mutable in memory. The durable source of truth is `SnapshotInfo` in `snapshotInfoTable`, where previous IDs are persisted and used to rebuild chains on startup.

Dependencies and integration points: It is used exclusively by `SnapshotChainManager` and test inspection helpers.

Risks and test signals: The class allows arbitrary mutation, so manager invariants must be enforced outside it. Tests should compare node equality before and after link rewrites and verify add/delete operations update both neighboring nodes.
