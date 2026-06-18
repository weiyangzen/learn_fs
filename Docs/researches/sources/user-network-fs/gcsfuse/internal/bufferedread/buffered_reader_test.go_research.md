# sources/user-network-fs/gcsfuse/internal/bufferedread/buffered_reader_test.go

## Purpose
This suite is the behavioral specification for the buffered read path around `BufferedReader`. It exercises construction, prefetch block reservation, queue invariants, fresh-start scheduling, foreground reads, background prefetch failures, fallback to another reader, and block lifetime under concurrent reads. The tests use deterministic fake readers that emit an A-Z byte pattern keyed by absolute offset, which makes block alignment and multi-block slicing observable.

## Important APIs, Types, And Functions
The suite type `BufferedReaderTest` owns common fixtures: a `gcs.MinObject`, mocked bucket, global block semaphore, `BufferedReadConfig`, static worker pool, noop metrics, and `gcsx.ReadTypeClassifier`. Helpers include `createFakeReaderWithOffset`, `assertBlockContent`, `assertReadResponseContent`, and `assertBufferContent`.

The tests directly exercise both public and package-private reader behavior: `NewBufferedReader`, `Destroy`, `CheckInvariants`, `scheduleNextBlock`, `scheduleBlockWithIndex`, `freshStart`, `prefetch`, and `ReadAt`. They also inspect internal fields such as `nextBlockIndexToPrefetch`, `randomSeekCount`, `numPrefetchBlocks`, `blockQueue`, `blockPool`, and callback-driven block `RefCount`.

## Control Flow And State
Construction tests verify the reader stores dependencies, creates a block queue and pool, initializes cancellable context state, reserves only the minimum useful number of blocks based on object size and `MinBlocksPerHandle`, and fails when the global semaphore cannot provide any block. Invariant tests intentionally corrupt queue length, random seek count, and prefetch block size to assert panics.

Scheduling tests show the reader calculates byte offsets from block indexes, submits urgent and non-urgent download tasks to the worker pool, sets absolute block offsets, advances `nextBlockIndexToPrefetch`, and leaves downloaded blocks in FIFO order. `freshStart` aligns arbitrary offsets down to a block boundary, schedules one urgent block plus initial prefetch blocks, caps by `MaxPrefetchBlockCnt`, stops at object end, and doubles `numPrefetchBlocks` for later sequential prefetch. `prefetch` respects queue capacity and available pool blocks; if the pool is exhausted, it does not advance scheduling state.

`ReadAt` tests cover EOF and empty-buffer returns, backward and forward seeks, queue discard/cancel behavior, multi-block reads, reads exactly to EOF, partial last-block reads, and the way sequential reads consume queued blocks and trigger more prefetch. Random reads increment `randomSeekCount`; after the threshold, the reader returns `gcsx.FallbackToAnotherReader` until the read classifier becomes sequential again, at which point the reader can reset and resume.

## State And Persistence Behavior
The state under test is in memory: prefetch queue contents, block-pool reservations, block readiness, cancellable download contexts, random-read counters, and callback-held reference counts. No persistent files are written by this test. The important lifetime rule is that returned `ReadResponse.Callback` releases block references; `Destroy` waits for callbacks before completing, and evicted in-use blocks are released only after the callback runs.

## Dependencies And Integration Points
The suite integrates `internal/block` prefetch blocks, `internal/gcsx` read requests/responses and read classification, `internal/storage` testify mocks, `internal/storage/fake` readers, `internal/workerpool`, `metrics.NewNoopMetrics`, `golang.org/x/sync/semaphore`, and `testify` assertions/suites. Mocked `Bucket.NewReaderWithReadHandle` calls validate GCS byte-range requests by `Range.Start` and sometimes `Range.Limit`.

## Risks And Edge Cases
The tests highlight risks around leaked semaphore permits, queue entries canceled while still in use, prefetch failures affecting unrelated foreground reads, mmap/block allocation failure, data races under concurrent reads, duplicate downloads for the same block, and stale fallback state after random access patterns. They also show that failed background prefetch is tolerated for the current read but becomes visible when the failed block is later read.

## Test Signals
Coverage is broad and high-signal for queue scheduling, fallback, concurrency, and resource release. The tests are mostly unit-level with mocked GCS and a real worker pool; they do not validate live Cloud Storage behavior or production timing, but they explicitly wait for block readiness to reduce races.
