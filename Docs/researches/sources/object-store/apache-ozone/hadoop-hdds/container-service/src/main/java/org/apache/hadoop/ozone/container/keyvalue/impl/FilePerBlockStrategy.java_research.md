# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/FilePerBlockStrategy.java

## Purpose
`FilePerBlockStrategy` implements `ChunkManager` for FILE_PER_BLOCK containers, storing all chunks of a block in one block file and supporting stream writes, reads, deletes, overwrite accounting, and file-channel caching.

## Important APIs, Types, And Functions
Main methods are `streamInit`, `getStreamDataChannel`, `writeChunk`, `readChunk`, `deleteChunk`, `deleteChunks`, `finishWriteChunks`, and `finalizeWriteChunk`. Nested `OpenFiles` caches `RandomAccessFile` channels with expire-after-access cleanup. Constructor state includes sync mode, read buffer settings, mmap manager, and Netty read toggle.

## Control Flow
Writes verify layout, skip empty chunks and COMMIT_DATA-only calls, get an open block channel, detect overwrite, validate append offset for new writes, write at chunk offset, account only file-growth delta for extending overwrites, and update container write stats. Reads select Netty, mmap, or normal buffer paths. Finish/finalize close cached handles and verify the file exists. Deletes remove the whole block file and reject partial range deletes.

## State And Persistence
It persists block files under the chunks directory and maintains an open-file cache. It updates container statistics and volume used-space accounting through `KeyValueContainerData`. Metadata cleanup is handled elsewhere.

## Dependencies And Integration Points
Dependencies include `ChunkUtils`, `FILE_PER_BLOCK` layout helpers, `KeyValueStreamDataChannel`, `MappedBufferManager`, `BlockManager`, `ContainerMetrics`, Guava cache, Hadoop `FileUtil`, and Ratis data channels. It is selected by `ChunkManagerDispatcher` and used by normal writes and reconciliation.

## Risks And Test Signals
Risks include stale cached channels after repair/replacement, append offset inconsistency, overwrite accounting bugs, partial delete rejection, sync behavior, and mmap resource limits. Tests should cover append, pure overwrite, extending overwrite, COMMIT_DATA no-op, stream writes, finish/finalize handle closure, full/partial delete, read variants, and IO-failure volume handling.
