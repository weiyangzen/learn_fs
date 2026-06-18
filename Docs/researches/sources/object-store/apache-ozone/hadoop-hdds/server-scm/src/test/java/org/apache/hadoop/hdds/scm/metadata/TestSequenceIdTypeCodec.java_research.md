# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/TestSequenceIdTypeCodec.java

Purpose: verifies persisted `SequenceIdType` enum encoding remains byte-compatible with the previous string-based representation.

Important APIs and types: `enumCodec = SequenceIdType.getCodec()` and `stringCodec = StringCodec.get()`. Tests iterate over every `SequenceIdType` value and compare exact bytes, decode legacy string bytes with the enum codec, decode new enum bytes with `StringCodec`, and run `CodecTestUtil.runTest()` for heap/direct byte buffer compatibility.

Control flow: every JUnit method loops across all enum values, so adding a new enum constant automatically receives coverage. Assertions enforce exact equality with `type.name()` encoded by `StringCodec`.

State and persistence: no database state. The persisted form is a byte array representing the enum name string. This matters for cluster upgrade and downgrade paths because existing RocksDB keys/values may have been written as strings.

Integration points and risks: protects the SCM sequence ID metadata table and any code that expects stable enum names on disk. Renaming enum constants or changing `getByteArray()`/codec behavior would break compatibility. The tests do not cover invalid names, nulls, or case normalization, which remain separate error-handling concerns.
