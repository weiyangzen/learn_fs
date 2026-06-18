# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/ha/io/TestScmListCodec.java

Purpose: negative test for `ScmListCodec` deserialization, ensuring list payloads without an element type are rejected with a useful protocol error.

Important APIs and types: the test builds an `SCMRatisProtocol.ListArgument` with a value but intentionally omits `type`. It constructs `ScmListCodec` with an empty `ScmCodecFactory.ClassResolver`, deserializes the protobuf `ByteString`, and expects `InvalidProtocolBufferException`.

Control flow: the single JUnit method uses `assertThrows`, then asserts the exception message contains `Missing ListArgument.type`. This checks both failure mode and diagnostic content.

State and persistence: no persistence. Inputs are in-memory protobuf messages. Dependencies include Ratis-shaded protobuf, `Collections.emptyList()`, and JUnit assertions.

Integration points and risks: `ScmListCodec` is used for SCM HA Ratis list arguments, so missing type metadata could otherwise decode ambiguously or fail later. The test only covers missing type, not unknown type names, malformed element payloads, empty lists, nested lists, or resolver collisions.
