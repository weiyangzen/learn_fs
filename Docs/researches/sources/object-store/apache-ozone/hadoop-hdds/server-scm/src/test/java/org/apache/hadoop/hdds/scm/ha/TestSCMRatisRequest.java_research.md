<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisRequest.java -->
# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisRequest.java

Purpose: This suite tests `SCMRatisRequest` encoding/decoding for replicated SCM method calls and its validation of malformed request protobufs.

Important APIs and types: It uses `SCMRatisRequest.of`, `encode`, `decode`, `SCMRatisProtocol.SCMRatisRequestProto`, `SCMRatisProtocol.MethodArgument`, `RequestType.PIPELINE`, `PipelineID`, `HddsProtos.PipelineID`, Ratis `Message`, `ByteString`, `UnsafeByteOperations`, and `InvalidProtocolBufferException`.

Control flow: Success tests encode/decode a protobuf pipeline ID argument, a list of pipeline ID protobufs, and a `Long`. Failure tests attempt to encode a non-protobuf `PipelineID`, decode a non-protobuf message, and decode request protos missing request type, method, method name, argument type, or argument value.

State and persistence behavior: There is no persistence. Runtime state is serialized request messages and decoded operation/argument arrays.

Dependencies and integration points: This protects the request serialization path used by SCM Ratis proxies and invokers. Explicit missing-field validation is especially important after proto3 migration.

Risks: Reflection-based argument decoding must stay aligned with allowed argument classes and collection codecs. Non-protobuf values should fail predictably rather than being silently corrupted.

Test signals: Successful round-trip equality for supported arguments and `InvalidProtocolBufferException` messages containing "Missing request type", "Missing method", "Missing method name", "Missing argument type", and "Missing argument value".
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/TestSCMRatisRequest.java -->
