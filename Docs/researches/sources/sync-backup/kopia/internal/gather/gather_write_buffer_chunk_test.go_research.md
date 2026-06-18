# sources/sync-backup/kopia/internal/gather/gather_write_buffer_chunk_test.go

Purpose: validates chunk allocator reuse, contiguous allocator sizing, and diagnostic allocation tracking.

Important APIs/types/functions: `chunkAllocator.allocChunk`, `releaseChunk`, `freeListHighWaterMark`, `maxContiguousAllocator`, `splitter.SupportedAlgorithms`, `DumpStats`, and `trackChunkAllocations`.

Control flow: `TestWriteBufferChunk` uses a small allocator, releases chunks, and asserts LIFO reuse by observing old bytes in reset-length slices. `TestContigAllocatorChunkSize` checks the max contiguous chunk can hold every supported splitter max segment size plus overhead. `TestTrackAllocation` enables tracking, logs stats before allocation, after append, and after close, and checks leaked-chunk diagnostics appear and disappear.

State/persistence behavior: all state is in-memory global allocator/test allocator state. The test temporarily mutates `trackChunkAllocations` and restores it with defer.

Dependencies/integration: integrates with `repo/splitter` to keep allocator sizing aligned with splitter algorithms. Uses logging to a buffer for diagnostics assertions.

Risks/test signals: the reuse test intentionally confirms old data remains in pooled capacity, documenting that callers cannot assume zeroed memory. It does not exercise concurrent allocator use.
