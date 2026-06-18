# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmIntegerCodec.java

Purpose: SCM HA codec for `Integer` values.

Important APIs and types: Implements `ScmCodec<Integer>` and delegates byte conversion to the shared DB `IntegerCodec`.

Control flow: Serialization wraps the newly allocated integer byte array in a shaded `ByteString`; deserialization reads bytes back through `IntegerCodec`.

State and persistence behavior: Stateless and used for HA message payloads.

Dependencies and integration points: Registered in `ScmCodecFactory`, notably for finalization layout feature ids and integer return values.

Risks and test signals: Compatibility depends on `IntegerCodec`'s stable byte format. Tests should cover min, max, zero, positive, negative, and malformed input behavior.
