# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerDownloader.java

Purpose: defines the pull-replication download contract for copying a raw container archive from one or more source datanodes into a local working directory.

Important APIs and types: `getContainerDataFromReplicas(long containerId, List<DatanodeDetails> sources, Path downloadDir, CopyContainerCompression compression)` returns the downloaded archive path or null when no source succeeds. The interface extends `Closeable` so implementations can own network clients or thread resources.

Control flow and state: none in the interface. Implementations decide whether to try sources sequentially, in random order, or in parallel.

Dependencies and integration: used by `DownloadAndImportReplicator` before `ContainerImporter.importContainer`. The concrete implementation here is `SimpleContainerDownloader`, which uses `GrpcReplicationClient`.

Risks and test signals: callers expect a complete local tarball and clean failure semantics. Tests for implementations should cover null/default download directories, compression propagation, retry ordering, partial file cleanup, and closing any underlying network clients.
