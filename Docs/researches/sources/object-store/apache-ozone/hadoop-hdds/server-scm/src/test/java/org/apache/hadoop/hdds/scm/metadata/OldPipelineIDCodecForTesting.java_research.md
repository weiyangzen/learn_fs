# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/test/java/org/apache/hadoop/hdds/scm/metadata/OldPipelineIDCodecForTesting.java

Purpose: test-only implementation of the legacy `PipelineID` RocksDB codec, used as a compatibility oracle for current `PipelineID.getCodec()` behavior.

Important APIs and types: implements `Codec<PipelineID>`. `toPersistedFormat(PipelineID)` writes a 16-byte UUID representation: most significant bits first, then least significant bits, each big-endian via `ByteBuffer.putLong`. `fromPersistedFormatImpl(byte[])` reads the two longs with `toLong(...)`, creates a `UUID`, and returns `PipelineID.valueOf(id)`. `copyObject()` is unsupported.

Control flow: encoding allocates a 16-byte array and copies two 8-byte arrays into it. Decoding validates each 8-byte segment length in `toLong`; short arrays throw `ArrayIndexOutOfBoundsException` with a specific size message.

State and persistence: no internal state. Its output shape models persisted SCM metadata bytes in RocksDB. Dependencies are `PipelineID`, `UUID`, `ByteBuffer`, and the HDDS `Codec` contract.

Integration points and risks: paired with `TestPipelineIDCodec` to ensure upgrades and downgrades can read existing pipeline IDs. Because it intentionally preserves old behavior, spelling mistakes or exception types should not be cleaned up casually if tests depend on exact legacy semantics. It does not implement object copying, so it should remain limited to compatibility tests.
