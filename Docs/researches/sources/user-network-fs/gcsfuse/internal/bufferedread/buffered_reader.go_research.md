<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedread/buffered_reader.go -->
# Research: sources/user-network-fs/gcsfuse/internal/bufferedread/buffered_reader.go

Purpose: implements a prefetching `gcsx.Reader` that serves sequential reads from mmap-backed in-memory blocks and falls back for random or memory-constrained access patterns.

Important APIs/types/functions: `BufferedReadConfig`, `BufferedReader`, `BufferedReaderOptions`, `NewBufferedReader`, `ReaderName`, `ReadAt`, `Destroy`, `CheckInvariants`, and helpers `handleRandomRead`, `prepareQueueForOffset`, `freshStart`, `prefetch`, `scheduleNextBlock`, `scheduleBlockWithIndex`, `callback`, and `releaseOrMarkEvicted`.

Control flow: construction reserves per-handle blocks from a global semaphore and initializes queue/pool state. `ReadAt` detects random seeks, clears stale queued blocks, starts urgent prefetch if needed, waits for the head block, returns zero-copy data slices plus a callback, and schedules more blocks as consumption advances. Random reads beyond threshold return `gcsx.FallbackToAnotherReader`; memory pressure during urgent block acquisition also falls back.

State and persistence: state is process-local and guarded by `mu`: block queue, block pool, next prefetch index, random seek count, prefetch window size, worker pool, and outstanding callback waitgroup. No data is persisted; downloaded ranges live in mmap blocks until returned to the pool or deallocated in `Destroy`.

Dependencies: common queue, block/prefetch pool, workerpool tasks, GCS bucket/object interfaces, metrics, tracing, read-type classifier, FUSE handle IDs, global semaphore, and `downloadTask` for actual object range reads.

Risks: zero-copy slices require FUSE callbacks to fire; otherwise `Destroy` may time out and leak blocks. Queue and pool are not thread-safe outside the reader lock. Cancellation relies on download tasks notifying block readiness. Random-read fallback thresholds and invariant `randomSeekCount <= threshold` must stay aligned.

Test signals: `buffered_reader_test.go` covers construction, reserved blocks, allocation failure, read paths, random read fallback, cleanup, and callback release behavior; `download_task_test.go` covers worker download status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedread/buffered_reader.go -->
