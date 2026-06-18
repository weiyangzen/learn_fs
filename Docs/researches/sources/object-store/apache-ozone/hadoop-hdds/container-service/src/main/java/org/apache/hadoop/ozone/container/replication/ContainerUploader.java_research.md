# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ContainerUploader.java

Purpose: abstracts client-side push replication upload setup.

Important APIs and types: `startUpload(long containerId, DatanodeDetails target, CompletableFuture<Void> callback, CopyContainerCompression compression)` opens an `OutputStream` that the caller writes container archive bytes to. The callback completes when the remote side reports upload completion or failure.

Control flow and state: none locally. Implementations must bridge stream writes to the underlying transport and complete the callback exactly once.

Dependencies and integration: used by `PushReplicator`, with `GrpcContainerUploader` as the gRPC implementation.

Risks and test signals: callers block on the callback after copying data. Tests should cover callback completion on remote success/error, stream close propagation, compression field propagation, and cleanup when upload creation fails after a transport client is opened.
