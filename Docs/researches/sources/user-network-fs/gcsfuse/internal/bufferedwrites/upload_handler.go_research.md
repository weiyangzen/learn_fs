# sources/user-network-fs/gcsfuse/internal/bufferedwrites/upload_handler.go

## Purpose
`upload_handler.go` implements the asynchronous streaming uploader behind buffered writes. It owns the GCS writer, a bounded channel of full blocks, one uploader goroutine, error state, cancellation, finalization, rapid-write flushing, and block return to the pool.

## Important APIs, Types, And Functions
`UploadHandler` stores `uploadCh`, `wg`, block pool, `gcs.Writer`, atomic upload error, cancel function, `sync.Once` for uploader startup, bucket/object settings, chunk retry/timeout settings, block size, and trace handle. `CreateUploadHandlerRequest` carries construction dependencies. Key methods are `newUploadHandler`, `Upload`, `createObjectWriter`, `UploadError`, `uploader`, `uploadBlock`, `Finalize`, `ensureWriter`, `FlushPendingWrites`, `CancelUpload`, `AwaitBlocksUpload`, and `Destroy`.

## Control Flow And State
`Upload` increments the wait group, ensures a writer exists, starts `uploader` exactly once, and enqueues the block. `createObjectWriter` builds a `gcs.CreateObjectRequest`, creates a background context with propagated trace and cancel function, and chooses `CreateAppendableObjectWriter` for rapid-write append to an unfinalized object; otherwise it uses `CreateObjectChunkWriter`.

The uploader goroutine reads blocks from `uploadCh`, calls `uploadBlock`, releases each block to the pool, and marks the wait group done. `uploadBlock` ignores nil blocks, short-circuits if an upload error already exists, seeks the block to offset zero, copies to the GCS writer, suppresses `context.Canceled` as local unlink behavior, and stores converted GCS errors atomically.

`Finalize` waits for queued blocks, closes the upload channel, ensures a writer even for empty-file flows, and calls `bucket.FinalizeUpload`. `FlushPendingWrites` waits, ensures a writer, and calls `bucket.FlushPendingWrites` without closing the channel. `Destroy` drains queued blocks, marks wait-group work done, releases blocks, and closes the channel.

## State And Persistence Behavior
Data persists to GCS through the writer. Blocks are reused after upload regardless of success, so upload failure is represented separately in `uploadError`. The GCS writer and cancel function are initialized lazily and then retained. Finalize closes the channel; flush keeps the stream open for more writes.

## Dependencies And Integration Points
This file depends on `internal/block`, `internal/storage/gcs`, `logger`, `tracing`, `sync`, and `atomic.Pointer[error]`. It is created and driven by `buffered_write_handler.go` and delegates all object-writing semantics to the bucket interface.

## Risks And Edge Cases
Because `Upload` calls `wg.Add(1)` before `ensureWriter`, a writer-creation error path can leave wait-group accounting inconsistent if callers later wait on the same handler. Channel close order is also sensitive: `Finalize` closes `uploadCh`, so later `Upload` calls would panic. Error pointers store addresses of local error variables, which escape safely in Go but require care when changing code. Context cancellation is intentionally suppressed only for copy errors, not writer creation/finalize/flush errors.

## Test Signals
`upload_handler_test.go` covers writer selection, request parameters, multiple block upload and release, copy errors, finalize/flush error storage, cancel behavior, await behavior, and destroy drain behavior.
