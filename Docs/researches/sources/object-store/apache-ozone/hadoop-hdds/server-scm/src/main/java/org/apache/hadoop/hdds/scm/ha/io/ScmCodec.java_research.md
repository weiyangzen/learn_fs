# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmCodec.java

Purpose: Minimal serialization contract for objects carried in SCM HA Ratis messages.

Important APIs and types: Generic methods `serialize(T object)` and `deserialize(ByteString value)` use Ratis shaded protobuf `ByteString` and can throw shaded `InvalidProtocolBufferException`.

Control flow: Implementations convert a supported Java/protobuf type to bytes and back; `ScmCodecFactory` selects implementations by resolved type.

State and persistence behavior: The interface has no state. Encoded data is persisted indirectly when requests are stored in the Ratis log.

Dependencies and integration points: Used by `SCMRatisRequest`, `SCMRatisResponse`, and all concrete `Scm*Codec` classes.

Risks and test signals: Codec implementations define HA wire compatibility. Tests should assert round trips for every registered type and failure behavior for malformed bytes.
