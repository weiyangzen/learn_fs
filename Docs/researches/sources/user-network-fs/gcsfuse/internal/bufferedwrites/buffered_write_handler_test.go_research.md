# sources/user-network-fs/gcsfuse/internal/bufferedwrites/buffered_write_handler_test.go

## Purpose
This suite specifies the buffered write handler's externally visible behavior: sequential writes, inode-visible file info, upload failure handling, sync versus flush semantics, grow-truncate behavior, and cleanup on destroy/unlink.

## Important APIs, Types, And Functions
`BufferedWriteTest` creates a fake bucket, global semaphore, and `BufferedWriteHandler` via `NewBWHandler`. It uses `fake.NewFakeBucket`, `storageutil.ReadObject`, generated random data, and mocked buckets/writers for size-mismatch paths. The suite frequently casts to `*bufferedWriteHandlerImpl` to inspect `current`, `totalSize`, `truncatedSize`, `uploadHandler.uploadCh`, and block pool free counts.

## Control Flow And State
Basic write tests show empty and non-empty writes update `WriteFileInfo`, block-size and multi-block writes advance `totalSize`, and writes with offsets less or greater than expected return `ErrOutOfOrderWrite` without changing size. Upload errors stored in `uploadHandler.uploadError` cause later `Write`, `Sync`, and `Flush` to fail.

Flush tests verify current-block upload, empty object creation, asynchronous error propagation, returned-object size validation across non-zonal, zonal, and Pirlo rapid-write variants, and repeated flush failure after an upload error. Sync tests verify full and partial blocks are uploaded, rapid-write buckets return a visible object after `FlushPendingWrites`, non-rapid buckets do not expose an unfinalized object, and size mismatch is rejected.

Truncate tests cover writing at the truncate offset, writing after truncating beyond current size, rejecting truncation below current size, zero-filling on flush, `WriteFileInfo` returning the max of total and truncate sizes, and rejecting stale writes at an old truncate position after later writes pass it.

Cleanup tests verify `Destroy` drains queued blocks and `Unlink` cancels active upload context and frees upload buffers while preserving one semaphore reservation for the last block.

## State And Persistence Behavior
The suite observes in-memory handler state and fake-bucket object contents. For rapid writes, `Sync` persists visible data to the fake bucket and returns object metadata. For non-rapid buckets, sync uploads chunks but does not finalize the object, so backdoor reads fail with `gcs.NotFoundError`.

## Dependencies And Integration Points
The tests integrate fake and mocked storage buckets, mocked writers, `gcs.BucketType` including zonal and Pirlo rapid-write states, tracing noop handles, global block semaphores, and integration-test random data helpers.

## Risks And Edge Cases
Important covered risks include size mismatch after GCS finalization/flush, upload errors that occur between writes, accidental backwards writes after grow-truncate, and semaphore leaks on unlink. The tests do not directly assert trace spans or logger output.

## Test Signals
The suite gives strong unit and fake-storage coverage for handler-level semantics. It complements `upload_handler_test.go`, which tests the lower async uploader directly.
