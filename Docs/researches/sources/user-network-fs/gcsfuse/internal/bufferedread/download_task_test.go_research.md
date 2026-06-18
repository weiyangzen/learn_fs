# sources/user-network-fs/gcsfuse/internal/bufferedread/download_task_test.go

## Purpose
This suite verifies `downloadTask.Execute` as the unit boundary between GCS range reads and prefetch block readiness. It ensures correct request construction, copied byte counts, failure propagation, cancellation classification, and clobbered-file error mapping.

## Important APIs, Types, And Functions
`DownloadTaskTestSuite` sets up a `gcs.MinObject`, `storage.TestifyMockBucket`, `block.GenBlockPool[block.PrefetchBlock]`, and noop metrics. Helpers include `getReadCloser` and `ctxCancelledReader`, a reader that returns `context.Canceled` during `Read`.

The tests instantiate `downloadTask` directly and call `Execute`, then inspect the destination block with `Size`, `Cap`, and `AwaitReady`.

## Control Flow And State
The success test expects `NewReaderWithReadHandle` to receive a `ReadObjectRequest` with object name, generation, and `[0,testBlockSize)` range, then verifies that copied content makes the block size equal to the test content and that block status becomes `BlockStateDownloaded`.

Failure tests cover reader creation returning a generic error, context deadline exceeded from the server, context canceled during reader creation after client cancellation, context canceled while copying from the reader, and `gcs.NotFoundError`. All failures notify `BlockStateDownloadFailed`; the NotFound case must wrap as `gcsfuse_errors.FileClobberedError`.

## State And Persistence Behavior
The suite uses an in-memory block pool and mocked/fake readers. There is no disk persistence. The observable state is block content, block status, and mocked bucket call count.

## Dependencies And Integration Points
The tests rely on the block prefetch pool, storage testify mock, fake reader wrapper, `gcs.ReadObjectRequest`, `workerpool.Task` embedding, `metrics.NewNoopMetrics`, `testify/suite`, and `semaphore.NewWeighted` for block pool construction.

## Risks And Edge Cases
The tests pin down cancellation as a failed block rather than a silent success. They also demonstrate that deadline exceeded is treated as ordinary failure, while client-side canceled contexts are still propagated as errors. They do not assert metrics values or reader close behavior.

## Test Signals
The suite gives strong signal for request range construction and block notification semantics. It is focused unit coverage and intentionally avoids running through `BufferedReader`.
