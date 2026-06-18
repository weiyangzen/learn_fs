## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreWithIncrementalChunkList.java

Purpose: Extends the datanode store to support incremental chunk-list updates where the latest partial chunk is stored separately until it becomes complete or the block ends.

Important APIs and functions: `getCompleteBlockData()` merges block data and last-chunk info. `reconcilePartialChunks()` validates offsets and appends the saved partial chunk. `putBlockByID()` routes old-client/full writes to the block table, full/eob incremental updates through `moveLastChunkToBlockData()`, and partial updates through `putBlockWithPartialChunks()`.

Control flow and state: Incremental blocks are identified by `INCREMENTAL_CHUNK_LIST` metadata. A full last chunk or end-of-block moves accumulated partial data into the main block table and deletes last-chunk state. A non-final partial write updates the last-chunk table and may insert an empty block entry for compatibility with utilities expecting block-table presence.

Persistence and dependencies: Uses the main block data table and `last_chunk_info` table in schema two/three. Depends on `BlockManagerImpl.FULL_CHUNK` metadata, `KeyValueContainerData` key generation, `BlockData`, and protobuf chunk metadata.

Risks: Offset validation is strict and throws if the saved partial chunk does not follow the block table's last full chunk. Mutating `BlockData` chunk lists in place can surprise callers holding references. The compatibility empty block entry has metadata but no chunks. Missing last-chunk table would break this class.

Test signals: Old-client overwrite, first partial chunk, repeated partial replacement, multiple chunks with final partial, full last chunk promotion, end-of-block promotion with empty data, missing block plus last-chunk lookup, offset mismatch failure, and BCSID propagation.
