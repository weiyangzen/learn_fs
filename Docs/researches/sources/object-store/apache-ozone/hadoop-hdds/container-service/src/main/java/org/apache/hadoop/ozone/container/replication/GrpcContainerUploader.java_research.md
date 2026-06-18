# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/GrpcContainerUploader.java

Purpose: implements `ContainerUploader` by opening a gRPC upload stream to a target datanode and returning an `OutputStream` that sends `SendContainerRequest` messages.

Important APIs and functions: `startUpload` optionally reads the local container's `bytesUsed` from `ContainerController` and sends it in the first request for better target-side reservation. It creates a `GrpcReplicationClient`, wraps the request stream in `WrappedRequestStreamObserver`, creates a `SendContainerOutputStream`, and closes the client when the stream closes. `createReplicationClient` uses the target replication port and security config. `SendContainerResponseStreamObserver` completes the provided future on server completion or error. `WrappedRequestStreamObserver` forwards calls while surfacing response-side errors from `isReady`.

Control flow and state: the upload stream is bidirectional: outgoing archive chunks flow through the returned stream while response observer completes the callback. Transport clients are closed on construction failure and on output close.

Dependencies and integration: used by `PushReplicator`. It depends on gRPC stubs, `ContainerController`, TLS/security config, and `SendContainerOutputStream`.

Risks and test signals: response errors must break producer writes promptly, and client cleanup must occur exactly once. Tests should cover missing local container size, first-message size field, server error before/after writes, callback completion, close cleanup, and wrapped observer propagation.
