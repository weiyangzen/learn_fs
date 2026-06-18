<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodecBufferCodec.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodecBufferCodec.java

Purpose: tests `CodecBufferCodec` conversion behavior for direct and heap-backed `CodecBuffer` values.

Important APIs/types/functions: `CodecBufferCodec.get(boolean direct)`, `fromCodecBuffer`, `fromPersistedFormat`, `CodecBuffer.allocateDirect`, `CodecBuffer.asReadOnlyByteBuffer`, `getArray`, and `StringCodec`.

Control flow: parameterized tests run for direct/non-direct modes. `fromCodecBuffer` verifies the codec returns the same buffer instance. Persisted-format tests decode string bytes into a buffer and then use `StringCodec` to recover the string. Byte-array allocation tests check resulting length, directness rules, and byte-array equality.

State and persistence behavior: state is transient buffer memory. Buffers are closed with try-with-resources to avoid leaks.

Dependencies and integration points: validates codec behavior used when DB layers persist or retrieve raw `CodecBuffer` values.

Risks: ownership semantics are important because `fromCodecBuffer` returns the same object rather than copying. Directness behavior for zero-length buffers is explicit and must remain stable.

Test signals: asserts same-object return, string round trip, buffer remaining length, direct vs heap allocation expectations, and exact array contents.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/utils/db/TestCodecBufferCodec.java -->
