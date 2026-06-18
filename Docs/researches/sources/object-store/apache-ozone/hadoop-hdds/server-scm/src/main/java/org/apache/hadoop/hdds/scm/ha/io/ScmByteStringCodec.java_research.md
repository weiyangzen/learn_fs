# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmByteStringCodec.java

Purpose: Pass-through codec for Ratis shaded protobuf `ByteString` values.

Important APIs and types: Implements `ScmCodec<org.apache.ratis.thirdparty.com.google.protobuf.ByteString>`.

Control flow: `serialize` returns the input object; `deserialize` returns the input bytes unchanged.

State and persistence behavior: Stateless. It preserves bytes inside HA request/response payloads without conversion.

Dependencies and integration points: Registered in `ScmCodecFactory` for shaded `ByteString` values. Distinct from `ScmNonShadedByteStringCodec`, which handles `com.google.protobuf.ByteString`.

Risks and test signals: Shaded/non-shaded ByteString confusion is the primary risk. Tests should assert factory resolution picks the correct codec for both classes and that bytes are preserved exactly.
