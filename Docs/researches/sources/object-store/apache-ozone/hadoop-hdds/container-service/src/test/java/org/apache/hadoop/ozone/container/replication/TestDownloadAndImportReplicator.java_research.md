## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestDownloadAndImportReplicator.java

Purpose: Tests that `DownloadAndImportReplicator` releases reserved committed space when download/import replication fails.

Important APIs/types/functions: `DownloadAndImportReplicator.replicate`, `SimpleContainerDownloader.getContainerDataFromReplicas`, `ContainerImporter`, `MutableVolumeSet`, `HddsVolume.getCommittedBytes`, `ReplicationTask`, and container size config.

Control flow: Setup builds real volume/importer infrastructure with mocked downloader. The test blocks downloader failure behind a semaphore after space reservation, verifies committed bytes rise by twice the container max size, releases the failure, then waits for committed bytes to return to the initial value.

State and persistence behavior: Uses a temporary data volume and committed-byte accounting. No successful container import is persisted.

Dependencies and integration points: Couples downloader failure handling to importer reservation semantics and volume accounting.

Risks and test signals: Uses async `CompletableFuture` and wait loops, so timeout tuning matters. It is a focused guard against leaked reservations after failed replication.
