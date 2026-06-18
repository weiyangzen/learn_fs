# sources/user-network-fs/rclone/backend/sharefile/upload.go

## Purpose

`upload.go` implements ShareFile large-file uploads for the main backend. It handles chunk calculation, buffering, per-chunk MD5, streamed versus threaded upload methods, finalization, and cleanup of upload responses.

## Important APIs, Types, and Functions

`largeUpload` stores upload context, parent `Fs`, target `Object`, source reader, accounting wrapper, total size, part count, ShareFile upload specification, thread count, and method mode. `newLargeUpload` validates the API method and prepares accounting. `transferChunk` posts one chunk to `ChunkURI` with index, offset, chunk hash, and final file hash when finishing. `finish` posts `FinishURI` for threaded uploads. `Upload` reads fixed-size buffers from the `Fs` token pool, hashes the whole file, dispatches chunks, collects errors, and finalizes. `parseUploadFinishResponse` validates ShareFile's completion payload through `Object.checkUploadResponse`.

## Control Flow

For known-size inputs, part count is computed from `ChunkSize`; unknown size uses streaming semantics. `Upload` loops until EOF, checks asynchronous error state, obtains a reusable buffer, fills it with `readers.ReadFill`, updates the whole-file MD5, and sends the chunk inline for streamed mode or in a goroutine for threaded mode. The final chunk adds `finish=true`, `fileSize`, and `fileHash`. After all workers finish, the code checks expected size, drains any worker error, and calls `finish` regardless of earlier errors.

## State and Persistence Behavior

Upload state is in memory. Buffers are borrowed from `Fs.bufferTokens` and must be returned at full configured capacity. ShareFile-side temporary upload state persists until the remote API finishes or abandons it.

## Dependencies and Integration Points

It depends on ShareFile API upload specification/finish types, rclone accounting wrappers, `readers.ReadFill`, the backend pacer/rest client, and object metadata validation in `sharefile.go`.

## Risks and Edge Cases

The `threads` field is computed but not directly used to bound goroutines here; actual concurrency is bounded by the buffer-token pool. The size error message appears to reverse expected/read values. Retrying all chunk errors after upload start can duplicate chunk posts depending on ShareFile idempotency. `finish` runs even after chunk errors, which may produce secondary errors or remote partial state.

## Test Signals

Integration chunked upload tests should cover known and unknown sizes, non-power-of-two final chunks, streamed and threaded server methods, remote MD5 validation, short reads, and failures that should cleanly report rather than corrupting the object.
