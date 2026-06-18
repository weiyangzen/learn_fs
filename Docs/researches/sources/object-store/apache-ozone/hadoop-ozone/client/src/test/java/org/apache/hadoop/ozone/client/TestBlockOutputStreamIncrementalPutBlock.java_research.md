# sources/object-store/apache-ozone/hadoop-ozone/client/src/test/java/org/apache/hadoop/ozone/client/TestBlockOutputStreamIncrementalPutBlock.java

## Purpose
This JUnit test verifies `BlockOutputStream` behavior when the client writes and hsyncs repeatedly with incremental chunk-list support both enabled and disabled.

## Important APIs, Types, And Functions
`parameters` supplies `true` and `false` for incremental chunk lists. `init` configures `OzoneClientConfig` with incremental chunk list and CRC32C checksums, enables hsync/HBase enhancements, sets bytes-per-checksum, and creates an `OzoneClient` whose `RpcClient` injects `MockOmTransport` and `MockXceiverClientFactory`. `writeSmallChunk` writes a 1 KiB buffer 4097 times with hsync after each write. `writeLargeChunk` writes a 1 MiB plus 1 byte buffer four times with hsync.

## Control Flow
Each parameterized test initializes the mock client, creates volume and bucket, writes repeated buffers through `bucket.createKey`, calls `hsync` after each write, closes the stream, then reads the key back sequentially and asserts each buffer matches.

## State And Persistence Behavior
Test state is local fields for client, key, volume, bucket, and in-memory configuration. Mock OM persists key metadata in `MockOmTransport`; mock datanodes persist chunks in `MockDatanodeStorage`. `@AfterEach` closes the client.

## Dependencies And Integration Points
This test integrates `RpcClient`, `OzoneOutputStream`, `OzoneInputStream`, mock OM/datanode classes, `OzoneClientConfig`, and hsync flags. It is an important signal for `MockDatanodeStorage.putBlockIncremental` and stream hsync semantics.

## Risks And Edge Cases
The read loop reuses `ByteBuffer` objects without explicit `clear`, relying on stream read behavior and full-buffer reads. The mock storage uses assertions for offset correctness. It does not test interrupted hsync, partial reads, or concurrent writes.

## Test Signals
The two parameterized methods cover incremental and non-incremental chunk list modes for small repeated hsyncs and large chunk-spanning hsyncs.
