# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmNonShadedGeneratedMessageCodec.java

Purpose: Generic codec for non-shaded protobuf `Message` types carried in SCM HA Ratis requests.

Important APIs and types: Parameterized by message type and constructed with a display name plus protobuf `Parser<T>`.

Control flow: Serialization wraps `object.toByteString().asReadOnlyByteBuffer()` in shaded Ratis bytes. Deserialization parses from the shaded byte buffer using the supplied non-shaded parser, converting parse errors to shaded `InvalidProtocolBufferException`.

State and persistence behavior: Holds parser/name only. Encoded message bytes become Ratis request/response payloads.

Dependencies and integration points: Registered by `ScmCodecFactory.putProto` for container, pipeline, deleted-block transaction, and summary protobuf messages.

Risks and test signals: Parser must match the registered class, and schema compatibility matters for Ratis logs. Tests should cover each registered proto type, malformed bytes, and error messages naming the failed proto.
