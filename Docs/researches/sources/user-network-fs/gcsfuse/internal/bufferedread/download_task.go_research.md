# sources/user-network-fs/gcsfuse/internal/bufferedread/download_task.go

## Purpose
`download_task.go` defines the worker-pool task that downloads one GCS object byte range into one prefetch block for buffered reads. It bridges `BufferedReader` scheduling with GCS range readers and block readiness notifications.

## Important APIs, Types, And Functions
`downloadTask` embeds `workerpool.Task` and stores the target `gcs.MinObject`, `gcs.Bucket`, metrics handle, destination `block.PrefetchBlock`, cancellation context, and optional zonal-bucket read handle. Its single method, `Execute`, implements the workerpool task contract.

## Control Flow And State
`Execute` derives the block id from `block.AbsStartOff()/block.Cap()`, logs start time, and defers completion handling. It computes the GCS range as `[AbsStartOff, min(AbsStartOff+block.Cap(), object.Size))`, calls `bucket.NewReaderWithReadHandle`, and passes object name, generation, byte range, gzip read behavior from `object.HasContentEncodingGzip()`, and any read handle. It then copies exactly `end-start` bytes into the block with `io.CopyN`.

The deferred completion path notifies the block as `BlockStateDownloaded` on success or `BlockStateDownloadFailed` with the error on failure. It distinguishes client cancellation for trace logging, converts `gcs.NotFoundError` from reader creation into `gcsfuse_errors.FileClobberedError`, wraps other reader/copy errors with phase context, closes the reader, and always records downloaded byte count through `GcsDownloadBytesCount`.

## State And Persistence Behavior
The task mutates only the destination prefetch block and metrics. Persistence is external: bytes are streamed from GCS into an in-memory or mmap-backed block supplied by the block package. The task does not retry, cache to disk, or own block release.

## Dependencies And Integration Points
The file depends on `internal/block` for destination block status, `internal/storage/gcs` for range reads and object metadata, `internal/fs/gcsfuse_errors` for clobber detection, `internal/workerpool` for task execution, `metrics` for read-byte accounting, and `logger` for trace/error messages. It is scheduled by the buffered reader and consumed by block awaiters.

## Risks And Edge Cases
The code assumes the block capacity and absolute offset define a valid object range. `io.CopyN` treats short reads as errors, so partial content or premature EOF marks the block failed. Metrics count bytes copied before failure, which is useful but can surprise callers expecting only successful bytes. A nil `metricHandle` or nil block would panic; callers are responsible for construction.

## Test Signals
`download_task_test.go` covers success, generic reader creation errors, deadline/cancel behavior, cancellation while reading, and NotFound-to-FileClobbered conversion. It validates block status notifications and range requests.
