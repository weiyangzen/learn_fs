# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/SnapshotChainManager.java

Purpose: `SnapshotChainManager` builds and maintains in-memory linked chains of snapshots: one global chronological chain and one chain per snapshot path. It provides navigation APIs used by snapshot diff, deletion, and snapshot metadata services.

Important APIs and types: It stores `globalSnapshotChain`, `snapshotChainByPath`, `latestSnapshotIdByPath`, `snapshotIdToTableKey`, `latestGlobalSnapshotId`, and `oldestGlobalSnapshotId`. Public methods include `addSnapshot`, `updateSnapshot`, `deleteSnapshot`, `removeFromSnapshotIdToTable`, global/path latest getters, global iterator, next/previous queries, `getTableKey`, and test accessors.

Control flow: Construction loads `snapshotInfoTable`, builds a map of snapshot IDs to `SnapshotInfo`, builds a previous-to-next map for global links, identifies the head, then walks forward calling `addSnapshot`. Adds validate non-duplication, head placement, known predecessors, and linear next-link constraints before updating neighbor nodes and latest pointers. Deletes validate neighboring links, remove the node, stitch previous and next nodes together, and update latest/oldest path/global pointers. All mutating public methods are synchronized and first validate that startup loading did not mark the chain corrupted.

State and persistence behavior: In-memory maps are rebuilt from `SnapshotInfo` persisted in RocksDB. This class does not itself persist chain changes; callers must update `snapshotInfoTable` consistently. `snapshotIdToTableKey` tracks table keys for snapshot lookup and rename updates.

Dependencies and integration points: It depends on `OMMetadataManager`, `SnapshotInfo`, `TableIterator`, and snapshot services. Snapshot deletion, diff iteration, purge, and snapshot rename code rely on its navigation and table-key mapping.

Risks and test signals: Startup load expects exactly one global head and a complete linear chain; branching, cycles, duplicate heads, or missing links mark the manager corrupted and all validation-gated APIs fail. Some getters return internal maps directly for tests. Tests should cover load corruption cases, add/delete in head/middle/tail positions, path-specific latest maintenance, iterator forward/reverse behavior, renamed snapshot table-key updates, and concurrent readers during synchronized mutation.
