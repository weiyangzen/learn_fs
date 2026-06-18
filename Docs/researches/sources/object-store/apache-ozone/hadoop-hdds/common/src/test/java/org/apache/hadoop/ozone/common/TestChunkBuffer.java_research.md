# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/ozone/common/TestChunkBuffer.java

## Purpose
Tests common `ChunkBuffer` behavior across byte-buffer, incremental, and list-backed implementations.

## Important APIs, types, and functions
- Uses `ChunkBuffer`, `ByteBuffer`, `ByteString`, `MockGatheringChannel`, `CodecBuffer`, and `CodecTestUtil`.
- Test cases include `testImplWithByteBuffer`, `testIncrementalChunkBuffer`, and `testImplWithList`.
- Helper assertions cover duplication, iteration, conversion to `ByteString`, and writing to channels/output streams.

## Control flow
The tests build buffers with random data, run a shared test routine across implementations, duplicate buffers, iterate chunks, convert to protobuf `ByteString`, and write through gathering channels while validating positions and content.

## State and persistence behavior
State is in-memory byte buffer content, positions, and chunk-buffer lifecycle. `CodecBuffer` cleanup is checked to avoid buffer leaks. No durable persistence.

## Dependencies and integration points
`ChunkBuffer` is used throughout Ozone chunk IO, checksum calculation, and protobuf conversion.

## Risks and test signals
Risks include incorrect buffer position handling, content loss across duplicate/iterate/write, and memory leaks. The tests provide broad implementation-contract coverage.
