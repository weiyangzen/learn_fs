# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/utils/RDBSnapshotProvider.java

## Purpose
`RDBSnapshotProvider` is an abstract RocksDB snapshot downloader for OM/SCM HA state transfer. It supports full and incremental snapshot flows by downloading tar parts from the current leader, untarring them into a candidate directory, and returning a `DBCheckpoint` when the Ratis snapshot completion flag appears.

## Important APIs and Types
Key APIs are the constructor, synchronized `init`, `downloadDBSnapshotFromLeader`, `checkLeaderConsistency`, `getSnapshotFileName`, `getCheckpointFromUntarredDb`, and abstract `downloadSnapshot`. Test hooks include `FaultInjector`, `getSnapshotDir`, `getCandidateDir`, `setInjector`, `getNumDownloaded`, and `getInitCount`.

## Control Flow and State
Construction creates `snapshotDir`, derives `candidateDir`, initializes atomics, and calls `init`. `init` ensures the parent exists, clears or creates the candidate dir, resets last leader, and increments init count. Downloads loop until a tar extraction contains `OZONE_RATIS_SNAPSHOT_COMPLETE`. Leader changes or unexpected candidate contents trigger cleanup and reset.

## Persistence, Dependencies, and Integration
The provider mutates filesystem directories under the configured snapshot directory, writes temporary tar files, deletes tar files after extraction, and returns `RocksDBCheckpoint` by default. It depends on `HAUtils.getExistingFiles`, `HddsServerUtil.ratisSnapshotComplete`, Hadoop `FileUtil`, and HDDS directory creation utilities. Subclasses provide the transport.

## Risks and Test Signals
The download loop is unbounded until a completion flag appears, so transport implementations and tests must simulate multipart termination. Candidate cleanup is leader-sensitive and critical for incremental correctness. Tests should cover leader change reset, stale candidate dir cleanup, snapshot filename uniqueness, tar deletion, incomplete multipart loops, injected pause, and subclass download failure propagation.
