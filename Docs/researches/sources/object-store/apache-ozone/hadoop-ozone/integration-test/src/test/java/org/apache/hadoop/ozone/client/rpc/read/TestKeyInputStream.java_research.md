<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestKeyInputStream.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestKeyInputStream.java

Purpose: This class verifies `KeyInputStream` composition, seeking, skipping, byte-array reads, direct `ByteBuffer` reads, EC reads, and continued reads after replica loss.

Important APIs/types/functions: It extends `TestInputStreamBase`, uses `ContainerLayoutTestInfo.ContainerTest`, `TestBucket`, `KeyInputStream`, `BlockInputStream`, `ChunkInputStream`, `BlockExtendedInputStream`, `ECReplicationConfig`, `XceiverClientMetrics`, `BufferUtils.getNumberOfBins`, OM `getKeyInfo`, and `TestHelper.countReplicas`/`waitForContainerClose`.

Control flow: `testNonReplicationReads` runs multiple cases in one layout-specific test. `testInputStreams` verifies key data is split into expected block streams and chunk streams with correct lengths. Random seek helpers repeatedly seek/read and validate slices against original data. `testECSeek` writes EC data and reads across EC chunk/block boundaries. `testSeek` and `testSkip` reset xceiver metrics, write three chunks, assert seek/skip do not issue `ReadChunk`, then read and verify exactly two chunks are fetched for a boundary-crossing read. Byte-array and `ByteBuffer` cases read full keys with many buffer sizes. `readAfterReplication` reads one byte, optionally `unbuffer`s, shuts down one pipeline datanode, and verifies remaining data can still be read.

State and persistence behavior: Persistent test state includes random keys with RATIS or EC replication and closed containers for replica tests. Runtime state includes stream position, internal part streams, xceiver read/write metrics, and client buffer contents.

Dependencies and integration points: Integrates Ozone key input stream logic, block/chunk stream generation, EC layout, SCM replica state, xceiver metrics, datanode shutdown, and buffer APIs.

Risks: Tests inspect internal stream structure and exact operation counts, so stream implementation changes can require updates. The replication read test shuts down a datanode and is ordered last to avoid shared-cluster side effects.

Test signals: Passing confirms key reads are correctly segmented, seeks/skips are lazy, all read APIs return exact bytes, EC offsets work, and open reads can continue after one replica disappears.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/read/TestKeyInputStream.java -->
