# sources/sync-backup/kopia/internal/gather/gather_write_buffer.go

Purpose: provides a thread-safe append-oriented buffer backed by pooled chunks and exposed as `gather.Bytes`.

Important APIs/types/functions: `WriteBuffer`, `Close`, `MakeContiguous`, `Reset`, `Write`, `AppendSectionTo`, `Length`, `ToByteSlice`, `Bytes`, `Append`, `Dup`, `NewWriteBuffer`, and `NewWriteBufferMaxContiguous`.

Control flow: `Append` lazily allocates a chunk, appends as much data as fits, and allocates additional chunks as needed. `MakeContiguous` resets the buffer and chooses the typical, max-contiguous, or raw allocation path based on requested length. `Close` and `Reset` release owned chunks to their allocator and invalidate old `Bytes` views.

State/persistence behavior: buffer state is in-memory and guarded by a mutex. `Bytes` returns the internal view, not a deep copy, so lifetime is tied to the buffer until `Dup` or `ToByteSlice` is used. `Dup` creates a new buffer with a contiguous copy.

Dependencies/integration: depends on `chunkAllocator` from `gather_write_buffer_chunk.go` and repository logging. Implements `io.Writer` for callers that stream into gather buffers.

Risks/test signals: forgetting to close buffers can retain chunks, especially with large contiguous allocators. `MakeContiguous` can allocate non-pooled memory for lengths larger than the max contiguous allocator and leaves `alloc` nil for that case.
