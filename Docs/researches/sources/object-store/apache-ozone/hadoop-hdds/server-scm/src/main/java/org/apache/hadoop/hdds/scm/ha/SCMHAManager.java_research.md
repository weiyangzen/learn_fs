# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAManager.java

Purpose: Top-level SCM HA service contract used by `StorageContainerManager` to own Ratis, snapshots, transaction buffering, membership changes, and checkpoint installation.

Important APIs and types: Lifecycle methods are `start`, `stop`, and `close`. Accessors expose `SCMRatisServer`, `SCMSnapshotProvider`, generic `DBTransactionBuffer`, and HA-specific `SCMHADBTransactionBuffer`. Operational APIs include `addSCM`, `removeSCM`, `downloadCheckpointFromLeader`, `getSecretKeysFromLeader`, `verifyCheckpointFromLeader`, and `installCheckpoint`.

Control flow: Implementations start HA transport and consensus services, route replicated writes through the returned Ratis server/buffer, and use checkpoint download/verify/install during follower catch-up.

State and persistence behavior: The interface defines persistence boundaries rather than state itself: DB transaction buffering, RocksDB checkpoints, Ratis `TermIndex`, and replicated secret keys.

Dependencies and integration points: Used by Ratis state machine callbacks, SCM bootstrap/add/remove commands, secret-key manager, snapshot provider, and metadata reload code.

Risks and test signals: Correctness depends on implementations honoring term-index checks before replacing the DB. Tests should cover membership validation, null snapshot-provider handling, checkpoint freshness checks, and proper type from `asSCMHADBTransactionBuffer`.
