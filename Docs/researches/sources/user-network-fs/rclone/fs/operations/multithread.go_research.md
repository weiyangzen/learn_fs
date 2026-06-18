# sources/user-network-fs/rclone/fs/operations/multithread.go

## Purpose
`multithread.go` implements chunked parallel object copying for large known-size transfers when the destination supports chunk or random-access writers and the source can satisfy ranged reads.

## Important APIs, types, and functions
- `doMultiThreadCopy` decides whether a transfer should use multi-thread copy based on config, source size, source/destination feature flags, cutoff, and local/local defaults.
- `multiThreadCopyState` holds source, size, chunk size, chunk count, accounting, and buffering mode.
- `copyChunk` performs a ranged read and writes one chunk.
- `calculateNumChunks` computes ceiling division for chunk counts.
- `multiThreadCopy` orchestrates writer setup, concurrency, abort behavior, metadata/modtime finalization, and destination lookup.
- `writerAtChunkWriter` adapts `fs.OpenWriterAt` into `fs.ChunkWriter`.
- `openChunkWriterFromOpenWriterAt` builds that adapter.

## Control flow
`multiThreadCopy` selects `OpenChunkWriter` or adapts `OpenWriterAt`. It disables buffering when the source is local, the writer does not seek, or the destination uses `OpenWriterAt`; otherwise each chunk is pre-read into a reserved multipart buffer. It opens the chunk writer, adjusts backend-provided chunk size and concurrency, limits concurrency to chunk count, and runs chunk goroutines under an `errgroup`. Each chunk opens a ranged source reader, accounts bytes, writes via `WriteChunk`, and reports failures. After all chunks complete, it closes the writer, finds the uploaded object, and for `OpenWriterAt` destinations sets metadata or modtime if needed.

## State and persistence behavior
The operation creates or overwrites a destination object. On error or process exit it aborts multipart state unless the backend requests leaving parts or upload completed successfully. For `OpenWriterAt` adapters, abort closes the writer and removes the temporary destination object. Accounting is attached to a single transfer account shared by chunk reads.

## Dependencies and integration points
It uses `fs.Features().OpenChunkWriter`, `OpenWriterAt`, `ChunkWriterDoesntSeek`, `NoMultiThreading`, metadata interfaces, `Open` from operations, accounting, `atexit`, multipart buffers, pool readers/writers, and `errgroup`. `copy.go` calls it from manual copy when eligible.

## Risks and edge cases
Unknown-size or zero-size objects cannot use this path. Backend-provided chunk size and concurrency can override config. Buffered mode reserves memory before opening source readers to avoid many blocked goroutines, but large concurrency/chunk sizes still carry memory pressure. Abort behavior must avoid deleting a pre-existing canary object when partial uploads are unsupported. Metadata setting may fail if destination lacks `SetMetadataer`.

## Test signals
`multithread_test.go` covers eligibility decisions, chunk-count calculation, actual multi-thread uploads/downloads around chunk boundaries, metadata preservation, backend chunk-size probing, and abort behavior when a later ranged read fails.
