# sources/sync-backup/kopia/repo/object/object_writer.go

Purpose: implements object writes on top of the content manager, including splitting, optional object-layer or content-layer compression, asynchronous content writes, checkpoints, and indirect index-object generation.

Important APIs/types/functions: `Writer` exposes `Write`, `Close`, `Checkpoint`, and `Result`. `objectWriter` tracks buffers, splitters, compression, prefix, indirect entries, async write semaphore, wait group, and stored write error. `WriterOptions` controls description, content ID prefix, data and metadata compressor names, splitter name, and async write concurrency. Helpers include `flushBufferLocked`, `prepareAndWriteContentChunk`, `maybeCompressedContentBytes`, `checkpointLocked`, and `writeIndirectObject`.

Control flow: `Write` holds `w.mu`, updates `totalLength`, uses `splitter.NextSplitPoint`, appends data to a gather buffer, and flushes at split points. `flushBufferLocked` reserves an indirect index slot and either writes synchronously or clones the buffer into an async goroutine gated by `asyncWritesSemaphore`. `prepareAndWriteContentChunk` decides whether compression belongs in content metadata or object bytes, writes content through `WriteContent`, and stores the resulting direct or compressed object ID in the indirect index. `Result` flushes any remaining or empty buffer and delegates to `checkpointLocked`; `Checkpoint` waits for async writes, returns empty for no flushed chunks, direct ID for one chunk, or writes a JSON index object and wraps it with an indirect ID.

State and persistence behavior: data chunks are persisted through `contentMgr.WriteContent`; indirect indexes are persisted as metadata-prefixed JSON objects when more than one chunk exists. Async write errors are stored and surfaced at checkpoint/result time. `Close` waits for async writes, closes splitter and gather buffer, and notifies the manager that the writer closed.

Dependencies/integration: depends on `gather` for reusable buffers, `content` for content IDs/prefixes, `compression` for compressors and header IDs, `splitter` for chunk boundaries, and manager methods such as `closedWriter` and `newDefaultSplitter`. Its indirect JSON is read by `LoadIndexObject` in `object_reader.go`.

Risks: async writes require careful index reservation before goroutine completion; missing a wait before checkpoint could return incomplete IDs, so `checkpointLocked` waits. Compression behavior changes with `SupportsContentCompression`, and metadata objects always move compression responsibility to the content layer. `Result` flushes an empty buffer for empty objects, so empty-object semantics depend on content manager behavior.

Test signals: object manager tests stress sync and async paths, checkpoint/result races, compression fallback, indirect metadata compression, write errors during sync flush, async flush, checkpoint, and faulty compressor registration.
