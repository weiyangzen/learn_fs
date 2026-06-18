# sources/sync-backup/kopia/internal/gather/gather_write_buffer_chunk.go

Purpose: implements chunk allocation, freelist reuse, allocation statistics, and optional leak tracing for gather write buffers.

Important APIs/types/functions: `chunkAllocator`, `allocChunk`, `releaseChunk`, `trackAlloc`, `dumpStats`, `DumpStats`, and globals `defaultAllocator`, `typicalContiguousAllocator`, `maxContiguousAllocator`, and `trackChunkAllocations`.

Control flow: allocation increments counters, reuses the last freelist entry when available, or creates a zero-length slice with configured capacity. Release ignores non-owned capacity, deletes active tracking metadata, increments freed counters, and stores reset slices until `maxFreeListSize` is reached. `DumpStats` logs allocator counters and active allocation stack snippets.

State/persistence behavior: allocator state is process-local global state. `activeChunks` is populated only when `KOPIA_TRACK_CHUNK_ALLOC` or tests enable tracking; it is intended for diagnostics, not persistence.

Dependencies/integration: uses `runtime`, `unsafe`, environment variables, and repository logging. Chunk sizes are tuned for normal buffers and encryption/splitter contiguous buffers.

Risks/test signals: release is capacity-based, so slices with matching capacity are accepted as pool-owned. Freelist entries are not zeroed, so callers must treat newly allocated chunks as length zero and overwrite before reading. Tracking uses unsafe slice pointers for diagnostics.
