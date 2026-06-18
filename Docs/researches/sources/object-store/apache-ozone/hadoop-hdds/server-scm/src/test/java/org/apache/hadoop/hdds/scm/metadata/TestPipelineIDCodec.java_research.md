# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/TestPipelineIDCodec.java

Purpose: validates `PipelineID` RocksDB serialization format and compatibility between legacy and current codecs.

Important APIs and types: the test owns `oldCodec = new OldPipelineIDCodecForTesting()` and `newCodec = PipelineID.getCodec()`. It checks all-zero UUID bytes, all-`0xFF` UUID bytes, 100 random UUIDs, and round-trip behavior through both codecs. `CodecTestUtil.runTest(newCodec, pid, 16, oldCodec)` verifies direct and buffer-oriented codec operations against the legacy implementation.

Control flow: `checkPersisting()` builds a `PipelineID`, encodes with old and new codecs, and compares against an expected 16-byte big-endian layout. `assertUuid()` verifies new bytes match old bytes and both codecs decode legacy bytes back to the same `PipelineID`.

State and persistence: no RocksDB instance is opened; persisted state is modeled as byte arrays. The expected format is exactly 16 bytes: UUID most significant long followed by least significant long, big-endian.

Integration points and risks: this is an upgrade/downgrade guard for SCM pipeline metadata. It catches endianness changes, length changes, and decode incompatibility. Random UUID coverage broadens byte-pattern signal, but malformed length/error behavior is only indirectly covered by the old codec.
