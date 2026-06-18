# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOMRatisSnapshots.java

Purpose: This HA test class validates OM Ratis snapshot installation behavior independent of checkpoint transfer format. It focuses on follower state reload while clients read or write, rejection of stale checkpoints, shutdown behavior on corrupted checkpoints, and cleanup after failed snapshot download.

Important APIs and types: The suite uses `MiniOzoneHAClusterImpl`, `OzoneManagerRatisServer`, `TransactionInfo`, Ratis `TermIndex`, `DBCheckpoint`, `RDBStore`, `RDBCheckpointUtils`, `OzoneManagerRatisUtils`, `ExitManager`, `FaultInjector`, `OMMetadataManager`, `SnapshotInfo`, `OmKeyArgs`, `OmKeyInfo`, `getINode`, and `OmSnapshotManager.getSnapshotPath`. Static helpers `writeKeys`, `createOzoneSnapshot`, and `checkSnapshot` are reused by the transfer-specific test class.

Control flow: Setup creates a three-OM HA cluster with two active OMs, small Ratis logs, and an object-store-layout bucket. Client-write and client-read tests advance leader log index while an OM is inactive, start the inactive OM, perform concurrent client operations, wait for install logs and term/index catch-up, then verify follower key-table state. Failure tests create old or corrupted checkpoints, arrange the checkpoint under `om.db`, call `installCheckpoint`, and assert rejection or simulated system exit. A download failure test injects an `IOException` during snapshot provider pause and waits for candidate directory cleanup.

State and persistence behavior: The file verifies OM DB checkpoint contents, active and snapshot RocksDB directories, follower candidate directories, Ratis term/index persisted in checkpoint transaction info, key table rows, and hard-link identity between active and snapshot SST files. Corruption is modeled by deleting alternating SST files from a checkpoint before install.

Dependencies and integration points: It connects OM HA lifecycle, Ratis snapshot install, RocksDB checkpoint parsing, Ozone client read/write paths, snapshot lookup, OM service restart/reload, log capture, and exit-manager behavior.

Risks: The tests depend on timing, log messages, filesystem hard links, and direct manipulation of checkpoint directories. Stale-checkpoint and corrupted-checkpoint scenarios encode precise install safety semantics that should change only with explicit design changes.

Test signals: Signals include log messages for aborted install, reloaded OM state, finished checkpoint install, stale-checkpoint rejection, RPC server stop on corrupted reload, exact `TermIndex` preservation, follower metadata rows for all written keys, successful client reads/writes after install, hard-link inode equality for live snapshot SSTs, and empty candidate directory after failed download.
