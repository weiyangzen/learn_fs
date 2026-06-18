# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmEnumCodec.java

Purpose: Generic SCM HA codec for protobuf-backed enum types implementing `ProtocolMessageEnum`.

Important APIs and types: Constructor accepts enum class and `forNumber` function, validates that every enum constant maps back from its protobuf number, then serializes/deserializes integer wire numbers.

Control flow: Serialization writes `object.getNumber()` through `IntegerCodec`. Deserialization reads an integer, applies `forNumber`, and throws `InvalidProtocolBufferException` if the number is unknown or bytes cannot be decoded.

State and persistence behavior: Holds enum class and lookup function; no persistence except Ratis payload bytes.

Dependencies and integration points: Used by `ScmCodecFactory` for lifecycle events/states, pipeline states, and node types.

Risks and test signals: Unknown enum numbers fail rather than mapping to an unknown value. Tests should cover all registered enum constants, malformed integer bytes, and unknown number rejection.
