# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMHAManagerImpl.java

Purpose: Production HA manager that wires SCM to Apache Ratis, inter-SCM gRPC checkpoint transfer, transaction-buffer flushing, SCM membership changes, and DB checkpoint replacement.

Important APIs and types: Builds `SCMHADBTransactionBufferImpl`, `SCMRatisServerImpl`, `SCMSnapshotProvider`, and `InterSCMGrpcProtocolService`. Key methods are `start`, `createStartTransactionBufferMonitor`, `downloadCheckpointFromLeader`, `getSecretKeysFromLeader`, `verifyCheckpointFromLeader`, `installCheckpoint`, `startServices`, `stopServices`, `addSCM`, and `removeSCM`.

Control flow: Startup starts Ratis, bootstrapped nodes with an empty group submit `AddSCMRequest` through `HAUtils.addSCM`, then starts gRPC and the transaction-buffer monitor. Snapshot install verifies the downloaded checkpoint transaction info against the local last-applied index, stops the metadata store, replaces the DB directory with a checkpoint, reloads SCM managers from the new tables, and deletes the backup.

State and persistence behavior: Owns persistent RocksDB replacement, Ratis term/index checks, transaction-buffer lifecycle, secret-key synchronization, and dependent manager reinitialization for sequence IDs, pipelines, containers, deleted blocks, service configs, certificates, and finalization state.

Dependencies and integration points: Integrates `StorageContainerManager`, `SCMDBDefinition`, `HAUtils`, `SCMMetadataStore`, `SecretKeyProtocolClientSideTranslatorPB`, `OzoneSecurityUtil`, and Ratis `TermIndex`.

Risks and test signals: Checkpoint rollback and exit behavior are high risk: corrupt checkpoints force DB restoration and process exit. Membership operations must reject mismatched cluster IDs. Tests should assert service stop/restart ordering, DB backup deletion, reinitialize calls, bootstrapped add behavior, and secret-key retrieval only when enabled.
