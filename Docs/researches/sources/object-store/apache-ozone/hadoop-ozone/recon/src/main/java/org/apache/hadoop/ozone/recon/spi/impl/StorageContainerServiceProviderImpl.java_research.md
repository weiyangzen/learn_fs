# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/spi/impl/StorageContainerServiceProviderImpl.java

Purpose: Implements `StorageContainerServiceProvider` by delegating SCM RPCs and downloading SCM RocksDB snapshots for Recon.

Important APIs: `getPipelines`, `getPipeline`, `getContainerWithPipeline`, `getExistContainerWithPipelinesInBatch`, `getNodes`, container count overloads, `getSCMDBSnapshot`, `getListOfContainerIDs`, and `getListOfContainerInfos`.

Control flow and persistence: most methods are thin wrappers over `StorageContainerLocationProtocol`. `getSCMDBSnapshot` locates the leader from SCM peer roles, builds a security client and `ReconCertificateClient`, downloads a tar checkpoint through `InterSCMGrpcClient`, untars it into the Recon SCM DB directory, deletes the tar, and returns a `RocksDBCheckpoint`.

Dependencies and integration: depends on SCM client protocol, `ReconUtils`, `ReconStorageConfig`, `ReconContext`, security config, Ratis peer roles, and filesystem storage under `RECON_SCM_SNAPSHOT_DB`. Recon SCM sync code uses this provider for container and snapshot state.

Risks: peer role parsing uses fixed colon indexes, making it sensitive to peer-role string format. Snapshot failure marks Recon health unhealthy and records `GET_SCM_DB_SNAPSHOT_FAILED`, but returns null, so callers must check. The catch block catches `Throwable`, which includes errors beyond recoverable IO. Security and gRPC setup are on the hot path for snapshot retrieval.

Test signals: `TestStorageContainerServiceProviderImpl` is the direct unit signal. Add tests for leader parsing, null return on download failure, tar cleanup, health-state update, and `getListOfContainerInfos` delegation.
