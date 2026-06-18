# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmBooleanCodec.java

Purpose: SCM HA codec for boxed `Boolean` values.

Important APIs and types: Implements `ScmCodec<Boolean>` and uses constant shaded `ByteString` values for `"true"` and `"false"`.

Control flow: Serialization returns the true constant when the object is true, otherwise the false constant. Deserialization compares the input to the true constant and returns `Boolean.TRUE`; every other value returns `Boolean.FALSE`.

State and persistence behavior: Stateless and used only for Ratis message payloads.

Dependencies and integration points: Registered in `ScmCodecFactory`; used when HA methods return or accept Boolean values, such as sequence-id CAS results.

Risks and test signals: Deserialization is permissive: malformed bytes decode to false rather than failing. Tests should cover true/false round trips and decide whether invalid bytes should remain false-compatible.
