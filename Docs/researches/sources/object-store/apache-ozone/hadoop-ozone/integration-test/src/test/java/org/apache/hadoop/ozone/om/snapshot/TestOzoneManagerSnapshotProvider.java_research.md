# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestOzoneManagerSnapshotProvider.java

## Purpose
`TestOzoneManagerSnapshotProvider` verifies that an HA Ozone Manager follower can download a DB checkpoint from the current leader through the OM snapshot provider, and that the downloaded checkpoint carries the same Ratis transaction index as the leader's current snapshot index.

## Important APIs, Types, and Functions
The test builds a 3-OM `MiniOzoneHAClusterImpl`, creates a volume and bucket through `OzoneClientFactory.getRpcClient`, resolves the leader with `OmTestUtil.getCurrentOmProxyNodeId`, and calls `followerOM.getOmSnapshotProvider().downloadDBSnapshotFromLeader(leaderOMNodeId)`. `getDownloadedSnapshotIndex(DBCheckpoint)` opens the checkpoint location as an `InodeMetadataRocksDBCheckpoint`, locates `OzoneConsts.OM_DB_NAME`, and reads `TransactionInfo` through `OzoneManagerRatisUtils.getTrxnInfoFromCheckpoint`.

## Control Flow, State, and Persistence
Setup enables OM HTTP because checkpoint download uses the leader's HTTP endpoint, starts a 3-node HA OM service, and creates initial metadata so the leader has a non-empty DB state. The test selects a follower from the leader peer list, downloads the checkpoint to follower-local storage, extracts the checkpoint transaction index from the RocksDB checkpoint's transaction-info table, and compares it with `leaderOM.getRatisSnapshotIndex()`. State under test is persisted OM RocksDB metadata and Ratis transaction metadata embedded in the checkpoint.

## Dependencies and Integration Points
This test integrates OM HA, OM HTTP snapshot transfer, RocksDB checkpoint layout, OM Ratis transaction metadata, and Ozone client volume/bucket APIs. It depends on mini-cluster leadership discovery and on the checkpoint provider returning a fully materialized checkpoint directory.

## Risks and Test Signals
Main risks are stale leader selection, HTTP-disabled transfer paths, checkpoint directory layout changes, and mismatches between Ratis snapshot index and checkpoint `TransactionInfo`. The signal is strong for leader-to-follower checkpoint correctness, but narrow: it does not validate follower installation of the checkpoint or multi-follower behavior.
