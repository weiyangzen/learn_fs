# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/SendContainerOutputStream.java

Purpose: adapts push-replication archive writes to `SendContainerRequest` gRPC messages.

Important APIs and functions: the constructor stores compression and optional total container size in addition to inherited stream state. `sendPart` builds a request with container ID, data, current offset, and compression. It sets the size field only on the first message when a size is available.

Control flow and state: offset and byte counting are inherited from `GrpcOutputStream`. This class does not set an EOF marker; completion is represented by closing the gRPC request stream.

Dependencies and integration: returned by `GrpcContainerUploader.startUpload` and consumed by `PushReplicator`.

Risks and test signals: target-side space reservation depends on first-message size propagation. Tests should verify offset values, size on first chunk only, no size when unknown, compression proto field, multi-buffer splitting, and behavior when first write is larger than the buffer.
