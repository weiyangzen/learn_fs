# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/storage/ECBlockOutputStream.java

## Purpose
`ECBlockOutputStream` specializes `BlockOutputStream` for one internal EC block. It writes chunks to a single datanode pipeline, manages EC block-group metadata, and attaches stripe checksum information where required.

## Important APIs and Types
It overrides `write(byte[], int, int)`, exposes `write(ByteBuffer)`, and provides EC-aware `executePutBlock` overloads for block group length with either peer block data or checksum bytes. It also overrides `executePutBlock(boolean, boolean)` to return a putBlock response future without Ratis commit watching. `getDatanodeDetails()` exposes the single target datanode.

## Control Flow
Writes wrap the caller data in `ChunkBuffer`, call `writeChunkToContainer`, and update written length. Before putBlock, the stream writes `BLOCK_GROUP_LEN_KEY_IN_PUT_BLOCK` metadata. For checksum propagation, it chooses checksum-bearing block data, trims checksum chunks based on `blockGroupLength` and EC chunk size, replaces current chunk `stripeChecksum` fields, or updates the final chunk checksum from a supplied `ByteString`. It then sends `putBlockAsync` and validates the response.

## State and Persistence Behavior
Additional state is the closest datanode and futures for current chunk and putBlock responses. Persistent effects are internal EC chunk writes and block metadata containing block-group length and stripe checksums. It inherits chunk list, checksum, token, and exception state from `BlockOutputStream`.

## Dependencies and Integration Points
Used by EC key/block write flows. It depends on `ECReplicationConfig`, container `BlockData`, `ChunkInfo`, `OzoneConsts.BLOCK_GROUP_LEN_KEY_IN_PUT_BLOCK`, and base async RPC helpers.

## Risks
Checksum selection is subtle: only parity and first replica behavior differs, and the method must handle empty chunks, dirty data, partial groups, and mismatched chunk counts. `maxDataSizeByGroup.get(blockGroupLength).get()` assumes matching block data exists. Unlike Ratis streams, commit index is returned as zero, so callers must not expect Ratis-style buffer release behavior.

## Test Signals
`TestBlockOutputStreamCorrectness` creates EC block output streams and validates EC checksum/block metadata behavior. Broader EC write tests should cover partial stripe and failure cases.
