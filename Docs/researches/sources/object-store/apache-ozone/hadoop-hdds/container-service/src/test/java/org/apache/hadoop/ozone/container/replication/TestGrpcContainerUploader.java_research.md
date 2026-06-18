## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestGrpcContainerUploader.java

Purpose: Tests `GrpcContainerUploader` lifecycle around starting uploads, response callbacks, errors, and client closure.

Important APIs/types/functions: `GrpcContainerUploader.startUpload`, `GrpcReplicationClient.upload`, `SendContainerRequest`, `SendContainerResponse`, `CompletableFuture<Void>` callback, and `CallStreamObserver`.

Control flow: A subject subclass injects a mocked `GrpcReplicationClient`. Success returns an observer whose `onNext` sends a normal response. Error test sends response observer `onError` after data is written. Immediate-error test has `upload` throw. All paths verify client closure, and error paths verify callback exceptional completion or thrown exception.

State and persistence behavior: In-memory streams and futures; no disk state.

Dependencies and integration points: Covers push replication upload handshake and failure propagation into `PushReplicator` completion futures.

Risks and test signals: `NoopObserver` always ready and does not exercise backpressure. Strong signal for resource cleanup on normal and exceptional paths.
