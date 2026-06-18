## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestGrpcReplicationService.java

Purpose: Integration tests for replication gRPC service download and push-upload paths using real `ReplicationServer`, container controller, volume, and key-value container setup.

Important APIs/types/functions: `ReplicationServer`, `GrpcReplicationService.download`, `SimpleContainerDownloader`, `GrpcContainerUploader`, `PushReplicator`, `OnDemandContainerReplicationSource`, `ContainerImporter.importContainer`, `CopyContainerRequestProto`, and `CopyContainerResponseProto`.

Control flow: `init` creates datanode details with replication ports, a real container, controller, mocked importer, and starts a replication server. `testDownload` downloads a closed container into a temp directory and checks generated tar naming. `testUpload` pushes a container to the same datanode and verifies importer receives the ID. `closesStreamOnError` injects a source that throws during copy and verifies response stream completion.

State and persistence behavior: Creates real temporary volume/container data and downloads one tar-like file into a temp directory. `pushContainerId` records imported ID through a mocked importer.

Dependencies and integration points: Exercises gRPC server/client, security config, datanode ports, container controller, downloader, uploader, and push replicator end to end.

Risks and test signals: Network port and temporary filesystem behavior can be environment-sensitive. Strong signal for protocol compatibility and stream cleanup.
