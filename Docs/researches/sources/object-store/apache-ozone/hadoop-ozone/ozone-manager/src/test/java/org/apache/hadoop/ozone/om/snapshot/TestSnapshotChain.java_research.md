# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotChain.java

## Purpose
`TestSnapshotChain` validates `SnapshotChainManager`, which maintains chronological global snapshot chains and per-bucket path chains. It covers add, delete, load-from-table, iterator behavior, and corruption detection.

## Important APIs, Types, and Functions
- `SnapshotChainManager.addSnapshot`, `deleteSnapshot`, `nextGlobalSnapshot`, `previousGlobalSnapshot`, `nextPathSnapshot`, and `previousPathSnapshot`.
- `getLatestGlobalSnapshotId`, `getOldestGlobalSnapshotId`, and `getLatestPathSnapshotId`.
- `SnapshotInfo` previous-id fields: `pathPreviousSnapshotId` and `globalPreviousSnapshotId`.
- `OMMetadataManager.getSnapshotInfoTable()` provides persisted source data for chain rebuild.

## Control Flow
Setup creates a temporary `OmMetadataManagerImpl` and a fresh chain manager. Helper `createSnapshotInfo` creates active snapshots for `vol1/bucket1`. Add/delete tests build three-node chains and validate forward/backward traversal. Load tests write snapshots to the snapshot info table, construct a new manager, and assert reconstructed links and iterator order. Invalid-chain parameterized cases create disconnected, cyclic, partial cyclic, and diverged previous-pointer maps, then verify the manager marks the chain corrupted and rejects add/delete operations.

## State and Persistence Behavior
Snapshot chain state is reconstructed from `SnapshotInfo` rows in the OM metadata table. Deletion mutates next nodes' previous pointers in the in-memory helper map to emulate production chain rewiring before calling `deleteSnapshot`. Corruption state prevents subsequent chain mutation.

## Dependencies and Integration Points
The test integrates with the OM metadata RocksDB-backed table and `SnapshotInfo` model. It verifies global and path-chain behavior used by snapshot deletion, diff ordering, defrag, and chain traversal.

## Risks and Edge Cases
- The manual `deleteSnapshot` helper mirrors production rewiring logic; if production deletion changes, test setup may need updating.
- The test covers one snapshot path for normal operations, with corruption cases focused on pointer topology rather than multi-bucket isolation.

## Test Signals
Passing means chain construction and traversal are stable across table reload, corrupted chains are detected, and mutation is blocked once corruption is found.
