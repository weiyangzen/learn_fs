# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/impl/TestFilePerBlockStrategy.java

## Purpose
`TestFilePerBlockStrategy` tests the file-per-block chunk layout and inherits the common chunk-manager contract. Its local tests focus on multi-write block files, partial reads, closed-container recovery writes, bytes-used accounting for overwrites and extensions, block persistence for closed containers, and checksum updates.

## Important APIs, types, and functions
The suite uses `ChunkManager.writeChunk`, `readChunk`, `deleteChunk`, `KeyValueHandler.writeChunkForClosedContainer`, `putBlockForClosedContainer`, `updateAndGetContainerChecksumFromMetadata`, `BlockUtils.getDB`, and `ContainerLayoutTestInfo.FILE_PER_BLOCK`. It also uses `ContainerTestHelper.getChunk`, `setDataChecksum`, `ChunkBuffer`, `ChunkBufferToByteString`, and `verifyAllDataChecksumsMatch`.

## Control flow
One test writes 1024 small ranges into the same block file at increasing offsets and reads the whole region back, comparing file hashes. Partial-read tests write a single chunk and read both full and sliced ranges. Closed-container tests first close a container through `markContainerForClose` and `closeContainer`, then allow recovery writes and block puts; the same operations are asserted to fail for non-closed states. Bytes-used tests write initial data, then overwrite from a midpoint with a longer buffer and expect only the extension delta to be charged.

## State and persistence behavior
The file-per-block strategy stores multiple logical chunks in one block file, so offset and length handling directly affects file size, volume used space, container `bytesUsed`, and `statistics.writeBytes`. Closed-container put-block tests inspect RocksDB block rows and metadata table bytes-used values after appending chunks and replacing the last chunk with a larger one. Container data checksum is updated after metadata changes and verified against persisted metadata.

## Dependencies and integration points
The tests integrate chunk IO, closed-container reconstruction, container state transitions, volume and metadata configuration, `MutableVolumeSet`, `ContainerSet`, DB stores, and checksum validation. They exercise recovery behavior that spans `KeyValueHandler`, `ChunkManager`, and `BlockManager`.

## Risks and edge cases
Covered risks include accepting partial delete with nonzero offset, corrupting readback across many writes, slicing wrong byte ranges, allowing recovery writes in non-closed states, double-counting overwrites, not charging extension deltas, stale data checksums, and block-count drift on repeated closed-container put-blocks.

## Test signals
Signals include SHA digest equality, ByteString equality for full/partial reads, protocol result `UNSUPPORTED_REQUEST`, IOException assertions for invalid states, exact bytes-used/statistics values, RocksDB row comparisons, and checksum verification.
