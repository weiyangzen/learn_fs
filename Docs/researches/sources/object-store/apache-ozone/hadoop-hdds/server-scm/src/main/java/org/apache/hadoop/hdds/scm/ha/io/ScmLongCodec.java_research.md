# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmLongCodec.java

Purpose: SCM HA codec for `Long` values.

Important APIs and types: Implements `ScmCodec<Long>` and delegates to shared DB `LongCodec`.

Control flow: Serialization wraps the `LongCodec` byte array in a shaded `ByteString`; deserialization converts the byte array back to a `Long`.

State and persistence behavior: Stateless, used in Ratis request/response serialization.

Dependencies and integration points: Registered for sequence-id allocation, transaction ids, and other long-valued replicated methods.

Risks and test signals: Stable byte ordering is delegated to `LongCodec`. Tests should cover min, max, zero, positive, negative, and invalid byte arrays.
