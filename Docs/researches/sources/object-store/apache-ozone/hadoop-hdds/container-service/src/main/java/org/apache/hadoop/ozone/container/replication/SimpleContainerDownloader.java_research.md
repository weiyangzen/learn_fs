# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/SimpleContainerDownloader.java

Purpose: sequential pull-replication downloader that tries source datanodes one at a time until a container archive download succeeds.

Important APIs and functions: `getContainerDataFromReplicas` defaults a null download directory to the JVM temp `container-copy` directory, shuffles sources, creates a `GrpcReplicationClient` for each datanode, starts `download`, waits for the future, returns the path on first success, and closes each client in a finally block. `shuffleDatanodes`, `createReplicationClient`, and `downloadContainer` are visible for testing. `close` is a no-op.

Control flow and state: the implementation is stateless apart from security/certificate configuration. Interrupted downloads log the error, restore interrupt status, and continue through loop handling as coded.

Dependencies and integration: used by `DownloadAndImportReplicator`, relying on `GrpcReplicationClient` and datanode replication ports.

Risks and test signals: blocking `future.get()` can wait indefinitely if the stream stalls. Tests should cover shuffled retry order, all-sources failure returning null, client close per attempt, default download directory, interrupt status preservation, and partial output cleanup delegated to `StreamDownloader`.
