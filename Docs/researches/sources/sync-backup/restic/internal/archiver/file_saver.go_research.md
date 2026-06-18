# sources/sync-backup/restic/internal/archiver/file_saver.go

Purpose: Implements concurrent file content saving for the archiver. It reads files, chunks them, uploads data blobs asynchronously, builds `data.Node` content references, and reports per-file statistics through futures and callbacks.

Important APIs and types: `fileSaver` owns a chunk buffer pool, `restic.BlobSaverAsync`, chunker polynomial, job channel, `CompleteBlob`, and `NodeFromFileInfo`. `newFileSaver` starts worker goroutines. `Save` enqueues a `saveFileJob` and returns a `futureNode`. `saveFile` performs the actual file-to-blobs pipeline. `TriggerShutdown` closes the job channel.

Control flow and state: Each worker reuses one chunker. `saveFile` calls `start`, builds a metadata node, checks that it is a file, resets the chunker, loops through chunks, reserves positions in `node.Content`, and calls `SaveBlobAsync`. A mutex guards shared `futureNodeResult`, stats, remaining upload count, and content assignment. The future completes only after the reader reaches EOF, the file is closed, `completeReading` has run, and all async uploads have returned.

Persistence and dependencies: Persistence is through the repository's blob saver. In-memory state includes buffer pool entries, per-job content arrays, counters, and callback status. Dependencies include `chunker`, `data`, `fs`, `restic`, `errgroup`, and context cancellation.

Integration points: The archiver uses this from `runWorkers` and `save` to save regular files. The returned `futureNode` is consumed by tree saving. Stats flow into snapshot summaries, and `CompleteBlob` supports progress accounting.

Risks and test signals: Risks include callback order, data corruption if buffers are released too early, deadlocks if async callbacks never fire, races around `remaining`, double completion, context cancellation after queueing, file close errors, and non-file metadata. Tests in `file_saver_test.go` and `archiver_test.go` cover concurrent saves, callbacks, stats, cancellation, and upload-failure behavior.
