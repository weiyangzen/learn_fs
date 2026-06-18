# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/io/ScmNonShadedByteStringCodec.java

Purpose: Bridges non-shaded protobuf `com.google.protobuf.ByteString` values into shaded Ratis `ByteString` HA payloads.

Important APIs and types: Public `ScmCodec<com.google.protobuf.ByteString>` implementation with pass-through byte wrapping between protobuf namespaces.

Control flow: Serialization wraps the non-shaded byte buffer using Ratis shaded `UnsafeByteOperations`. Deserialization wraps the shaded read-only byte buffer using non-shaded protobuf `UnsafeByteOperations`.

State and persistence behavior: Stateless. It preserves bytes for Ratis messages.

Dependencies and integration points: Registered in `ScmCodecFactory` for `StatefulServiceStateManager` configuration bytes.

Risks and test signals: ByteBuffer lifetime and namespace confusion are the main risks. Tests should assert byte equality, factory resolution, and no accidental use of the shaded `ScmByteStringCodec` for non-shaded values.
