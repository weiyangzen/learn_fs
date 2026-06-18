# sources/storage-engines/rocksdb/utilities/persistent_cache/block_cache_tier_file.cc

Purpose: implements persistent-cache file primitives: cache record serialization, random-access reads, buffered append-only writes, file deletion, and the async writer pool used by `BlockCacheTier`.

Important APIs and control flow: `CacheRecord` encodes `{magic, crc, key_size, value_size, key, value}` and verifies CRC on read. `RandomAccessCacheFile::Open/Read/ParseRec` wrap `FSRandomAccessFile` in `RandomAccessFileReader` and deserialize records by `LBA`. `WriteableCacheFile::Create` opens a new writable file and establishes a file reference. `Append()` expands buffer slabs, records the LBA, serializes the record into buffers, advances `disk_woff_`, sets EOF when max size is reached, and dispatches full buffers. `DispatchBuffer()` pads partial EOF buffers for alignment and hands them to `ThreadedWriter`; `BufferWriteDone()` cascades dispatch and closes/reopens the file for reads after EOF.

State and persistence: in-flight files keep data in `CacheWriteBuffer` slabs and serve reads from memory until closed. Closed files are reopened through the random-access path. `BlockCacheFile::Delete()` asks `Env` for size then removes the `.rc` file. `ThreadedWriter` reserves cache capacity before appending buffer chunks to the writable file.

Dependencies and integration: uses `Env`, `FileSystem`, `WritableFile`, `FSRandomAccessFile`, `RandomAccessFileReader`, CRC32C, logging, direct IO options, `CacheWriteBufferAllocator`, and `PersistentCacheTier::Reserve`. `BlockCacheTier` owns file creation, cache-id assignment, metadata insertion, and eviction.

Risks and test signals: `NewWritableCacheFile()` ignores the `use_direct_writes` parameter in the current implementation, despite `Create()` accepting it. `DispatchIO()` appends `io_size_` slices without trimming the final slice, relying on buffer padding/alignment. CRC errors print diagnostic data to stderr and return read failure. Most persistent-cache file stress tests are disabled, so active coverage is mostly through the DB persistent-cache path.
