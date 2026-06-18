<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSInputStream.java

## Purpose
Unit tests for byte-buffer read behavior and capability/unbuffer integration in `OzoneFSInputStream`.

## Important APIs, types, and functions
Tests cover `read(ByteBuffer)` for heap and direct buffers, empty streams, EOF streams, `CapableOzoneFSInputStream.hasCapability`, and `CryptoInputStream.unbuffer` forwarding to a mocked `KeyInputStream`.

## Control flow
Nested loops exercise stream lengths, buffer capacities, and initial positions. Expected content is generated from random bytes and compared after the read. EOF tests ensure buffer position remains unchanged. Crypto test builds a mocked codec/decryptor and verifies one `unbuffer` call reaches the key stream.

## State and persistence behavior
All streams are in-memory byte arrays or mocks. No Ozone state is used.

## Dependencies and integration points
The test validates Hadoop byte-buffer APIs, stream capability flags, Hadoop crypto wrappers, and Ozone `KeyInputStream` unbuffer behavior that matters for cache release under encrypted reads.

## Risks and test signals
Strong signal exists for normal `read(ByteBuffer)`, EOF behavior, and unbuffer forwarding. Gaps remain for positioned byte-buffer reads, `ExtendedInputStream` fast path, statistics increments, read-only buffers, and fallback behavior when `available()` is misleading.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-common/src/test/java/org/apache/hadoop/fs/ozone/TestOzoneFSInputStream.java -->
