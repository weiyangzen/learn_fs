<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestStreamBlockInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestStreamBlockInputStream.java

Purpose: This class tests the gRPC streaming block read path enabled by `OzoneClientConfig.setStreamReadBlock(true)`, including sequential reads, positioned reads, ByteBuffer reads, seeking, checksum-disabled reads, and empty-key behavior.

Important APIs/types/functions: It extends `TestInputStreamBase`, uses `MiniOzoneCluster`, `OzoneClientFactory`, `TestBucket`, `KeyInputStream`, `StreamBlockInputStream`, `ByteBuffer`, `OzoneClientConfig`, and `ContainerProtos.ChecksumType.NONE`. It also lowers noisy logger levels for common Ozone/Ratis components.

Control flow: `testReadKey` starts a fresh cluster, enables stream-read-block on a copied config, writes random keys of fixed and random lengths, validates positioned reads, and reads full data with many buffer sizes and optional random starting offsets. `runTestPositionedRead` compares ordinary seek/read with `readFully(position, ByteBuffer)` for edge and random positions. `testAll` writes data with checksums enabled, verifies full reads by byte array, one-byte loop, and ByteBuffer, validates random seek behavior and invalid block-stream seeks, checks zero-length key behavior, then repeats read/seek with checksum type `NONE`.

State and persistence behavior: Persistent state is random keys in temporary test buckets. Runtime state includes stream positions, duplicated ByteBuffers, and `StreamBlockInputStream` block length/position.

Dependencies and integration points: Integrates the stream-block read implementation, key-level read APIs, positioned read contract, checksum handling, empty-key OM metadata, and gRPC xceiver service.

Risks: The test creates separate clusters instead of using the base shared cluster for its main methods, increasing runtime. Random offsets and sizes broaden coverage but can make failures harder to reproduce without logged parameters.

Test signals: Passing means streaming block reads return exact bytes for sequential and positioned reads, maintain position after failed seeks, work with and without checksums, and represent empty keys as no part streams with EOF on read.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestStreamBlockInputStream.java -->
