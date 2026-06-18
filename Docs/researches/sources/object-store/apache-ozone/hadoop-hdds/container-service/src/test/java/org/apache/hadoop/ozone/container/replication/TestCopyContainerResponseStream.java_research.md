## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestCopyContainerResponseStream.java

Purpose: Concrete `GrpcOutputStreamTest` for `CopyContainerResponseStream`, the server-to-client download response stream.

Important APIs/types/functions: `CopyContainerResponseStream`, `CopyContainerResponseProto`, inherited gRPC stream tests, and `verifyPart`.

Control flow: `createSubject` constructs a response stream with observer, container ID, and buffer size from the base class. `verifyPart` checks each protobuf response carries the expected container ID, read offset, length, and data bytes.

State and persistence behavior: In-memory observer messages only.

Dependencies and integration points: Ensures download streaming semantics match the abstract framing contract used by replication downloads.

Risks and test signals: Relies on the abstract suite for most coverage. It catches field-mapping regressions in offsets and lengths.
