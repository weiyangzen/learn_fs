## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/TestSendContainerOutputStream.java

Purpose: Concrete `GrpcOutputStreamTest` for `SendContainerOutputStream`, the upload stream used for push replication.

Important APIs/types/functions: `SendContainerOutputStream`, `SendContainerRequest`, `CopyContainerCompression`, inherited stream framing tests, and `verifyPart`.

Control flow: Base tests verify byte framing. `usesCompression` parameterizes every compression enum, writes one buffer, closes the stream, and verifies the emitted request includes container ID, offset zero, data, and the compression proto.

State and persistence behavior: In-memory observer messages only.

Dependencies and integration points: Ensures push upload requests carry correct framing and compression metadata for `SendContainerRequestHandler`.

Risks and test signals: Good field-level protocol signal. Does not exercise actual compressed payload transformation because the tested stream records compression metadata and data bytes in request construction.
