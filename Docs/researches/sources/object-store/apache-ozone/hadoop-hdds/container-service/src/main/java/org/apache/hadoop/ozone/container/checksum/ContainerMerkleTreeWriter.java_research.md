# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/checksum/ContainerMerkleTreeWriter.java

## Purpose
Builder for deterministic container checksum Merkle trees from chunk checksum metadata, including live blocks and deleted-block markers.

## Important APIs, Types, And Functions
Public APIs include constructors for empty or existing tree, `addChunks`, `addBlock`, `setDeletedBlock`, `update`, `addDeletedBlocks`, and `toProto`. Nested writers aggregate block and chunk checksums. `CHECKSUM_BUFFER_SUPPLIER` uses CRC32C.

## Control Flow
Chunks are sorted by offset inside each block and blocks by block ID. Chunk leaves hash stored checksum bytes; block checksums hash block ID plus chunk checksums; container checksum hashes block checksums. Update merges deleted blocks from existing state so deletes converge and are not overwritten by later scans. Deleted block addition can compute or clear top-level checksum depending on whether a full tree existed.

## State And Persistence
In-memory state is a `TreeMap` from block ID to block writers and per-block `TreeMap` from chunk offset to chunk writer. Persistence happens only when a manager writes the resulting protobuf to disk.

## Dependencies And Integration Points
Depends on container protobufs, `ChecksumByteBufferFactory.crc32CImpl`, `BlockData`, and Ratis `ByteString`.

## Risks
Checksum semantics are order-dependent and rely on sorted maps. Duplicate chunk offsets overwrite previous values. Deleted-block convergence rules intentionally prevent undelete, which is correct for reconciliation but can preserve a mistaken delete marker. Very large containers allocate buffers proportional to block/chunk count.

## Test Signals
Signals include deterministic tree equality independent of insertion order, duplicate offset overwrite behavior, deleted-block merge behavior, top-level checksum clearing for partial deleted-block updates, and CRC32C aggregate values.
