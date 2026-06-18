# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestOmSnapshotManager.java

Purpose: Unit coverage for `OmSnapshotManager` snapshot gating, cache eviction, snapshot limit enforcement, hardlink restoration, checkpoint archive file classification, snapshot path construction, and idempotent checkpoint creation.

Important APIs and types: `OmSnapshotManager`, `OmSnapshot`, `SnapshotChainManager`, `OmSnapshotLocalDataManager`, `SnapshotInfo`, `RDBStore`, `DBStore`, `RDBBatchOperation`, `InodeMetadataRocksDBCheckpoint`, `OmSnapshotUtils.createHardLinkList`, `OMDBCheckpointServlet.processFile`, `OM_HARDLINK_FILE`, snapshot/checkpoint directory constants, `TypedTable`, and `HddsWhiteboxTestUtils`.

Control flow: setup starts an OM with filesystem snapshots enabled, cache size one, RocksDB snapshot metrics disabled, and max FS snapshots two. Cleanup removes snapshots from chain/table and YAML sidecars. Tests replace metadata tables with mocks where needed, create snapshot infos and checkpoints, fetch active snapshots to trigger eviction, set up leader/follower directory trees for hardlink restoration, call `processFile` with and without destination dirs, check static path construction, and create the same checkpoint twice to validate idempotent logging.

State and persistence: uses real temporary OM DB, snapshot checkpoint directories, candidate directories, SST-like files, hardlinks, snapshot chain state, and local YAML path cleanup. Some tests mutate metadata manager internals to mocked tables.

Dependencies and integration points: covers OM snapshot cache lifecycle, RocksDB checkpoint creation, metadata table lookup for volume/bucket/snapshot info, checkpoint servlet archive generation, follower checkpoint extraction, HA hardlink preservation, and snapshot count limits.

Risks and edge cases: cache eviction must close DB stores; disabling snapshots is unsafe when snapshot table is non-empty; snapshot limit uses both chain state and in-flight count; follower hardlink remapping must account for leader/follower directory layout differences; `processFile` must classify copied files, hardlink candidates, exclusions, and non-SST files correctly; repeated checkpoint creation should not fail.

Test signals: boolean safety-check results, mocked DBStore `close` on eviction, log message for skipped RocksDB metrics registration, `TOO_MANY_SNAPSHOTS` exception, inode equality after hardlink restoration, exact process-file map sizes and byte counts, deterministic snapshot paths with version suffixes, and idempotent log message on duplicate checkpoint creation.
