# sources/user-network-fs/gcsfuse/internal/bufferedwrites/buffered_write_handler.go

## Purpose
This file implements the high-level buffered write handler used by file writes before data is uploaded to GCS. It accepts sequential writes, packs bytes into reusable blocks, hands full or flushed blocks to `UploadHandler`, tracks file size and mtime, supports grow-only truncation by zero filling, and finalizes or syncs uploads.

## Important APIs, Types, And Functions
`BufferedWriteHandler` exposes `Write`, `Sync`, `Flush`, `SetMtime`, `Truncate`, `WriteFileInfo`, `Destroy`, and `Unlink`. `bufferedWriteHandlerImpl` stores the current block, block pool, upload handler, `totalSize`, `mtime`, and `truncatedSize`. `WriteFileInfo` reports the visible size and mtime. `CreateBWHandlerRequest` carries the object, bucket, block limits, retry/timeout values, global semaphore, and trace handle. `NewBWHandler` constructs the block pool and upload handler.

## Control Flow And State
`Write` first checks `UploadError`, then enforces sequential offsets except for a pending truncate offset before data has caught up. If writing exactly at `truncatedSize`, it calls `writeDataForTruncatedSize` to append zero bytes through the normal buffering path. `appendBuffer` lazily obtains a block, copies as much data as fits, uploads full blocks immediately, and updates `totalSize`. Once `totalSize` reaches `truncatedSize`, the truncate marker is reset to `-1`.

`Sync` uploads a non-empty current block, waits for all queued block uploads, and for rapid-write buckets calls `FlushPendingWrites` to make bytes visible without finalization. It verifies returned size against `totalSize`, clears free block memory without destroying the active reservation, and returns any asynchronous upload error.

`Flush` checks prior upload errors, zero-fills any pending grow-truncate, uploads the current block, calls `Finalize`, validates final object size, then clears the block pool more aggressively. `Destroy` destroys pending upload state and clears blocks. `Unlink` cancels uploads and releases free blocks while intentionally keeping the last block reservation until file-handle close.

## State And Persistence Behavior
Write state is in-memory until the upload handler writes to GCS. `totalSize` may include bytes already uploaded and bytes still buffered. `truncatedSize` is deferred state: no data is written at `Truncate` time, but later `Write` or `Flush` materializes zero bytes. `mtime` is metadata cached for inode attribute responses and is not uploaded here.

## Dependencies And Integration Points
The handler depends on `internal/block` for pooled buffers, `internal/storage/gcs` for bucket/object abstractions, `UploadHandler` for streaming writes, `semaphore.Weighted` for global block limits, `logger` for resource cleanup failures, and `tracing` for upload trace propagation via the upload handler. It assumes the inode lock serializes write operations, so it does not protect its fields with mutexes.

## Risks And Edge Cases
The largest correctness risks are out-of-order writes, stale truncate offsets, async upload failures surfacing on later calls, block-pool leaks, and rapid-write size mismatches. Zero filling is chunked in 1 MiB pieces to avoid allocating the full truncated gap. A nil or misconfigured bucket/trace/block semaphore would fail outside this file's checks.

## Test Signals
`buffered_write_handler_test.go` covers offset enforcement, block splitting, sync/flush behavior for regional and rapid-write buckets, grow-truncate zero filling, size mismatches, upload-error propagation, destroy/unlink release behavior, and reflushing after upload failure.
