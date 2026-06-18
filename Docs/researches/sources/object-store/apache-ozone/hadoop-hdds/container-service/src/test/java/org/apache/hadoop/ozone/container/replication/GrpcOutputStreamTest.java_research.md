## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/replication/GrpcOutputStreamTest.java

Purpose: Abstract reusable test suite for gRPC-backed `OutputStream` implementations that frame byte writes into protobuf messages.

Important APIs/types/functions: `GrpcOutputStreamTest<T>`, `createSubject`, `verifyPart`, `CallStreamObserver<T>`, `ByteString`, `getRandomBytes`, and helper write/concat methods.

Control flow: Tests mix single-byte writes and byte-array writes, exact buffer fills, buffer overflow into multiple responses, write-after-close rejection, and close completion. `verifyResponses` captures all `onNext` messages, slices expected byte ranges by configured buffer size, and requires each data field to be a `LiteralByteString`.

State and persistence behavior: In-memory random buffers and mocked stream observer only. `subject.close()` must emit `onCompleted` once.

Dependencies and integration points: Base class is extended by `TestCopyContainerResponseStream` and `TestSendContainerOutputStream`, enforcing identical framing semantics for download and upload streams.

Risks and test signals: Random buffer sizes/data broaden coverage but make exact reproduction less direct. It catches subtle copy/concat regressions in protobuf payload construction and post-close state handling.
