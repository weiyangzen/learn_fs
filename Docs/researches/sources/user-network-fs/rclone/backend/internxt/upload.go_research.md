# sources/user-network-fs/rclone/backend/internxt/upload.go

## Purpose
Implements Internxt multipart upload support through rclone's `fs.ChunkWriter` interface, including AES-CTR encryption per chunk, ordered encrypted-data hashing, part tracking, finalization, and Drive metadata registration.

## Important APIs, Types, and Functions
Sizing helpers are `checkUploadChunkSize`, `SetUploadChunkSize`, `checkUploadCutoff`, and `SetUploadCutoff`. `internxtChunkWriter` stores the `Fs`, remote/source, upload session, completed parts, target size, parent directory ID, final metadata, chunk size, hash sequencing state, and pending encrypted chunk buffers. Methods include `OpenChunkWriter`, `WriteChunk`, `recordCompletedPart`, `submitForHashing`, `Close`, and `Abort`. `hashWriter` adapts session hashing to `io.Writer`.

## Control Flow
`OpenChunkWriter` rejects files below cutoff, calculates chunk size for known-size files, warns once for streaming uploads, ensures the parent directory exists, creates a `buckets.ChunkUploadSession`, and returns writer info with configured concurrency.

`WriteChunk` creates a cipher stream at the chunk byte offset, encrypts plaintext into an in-memory multipart buffer, uploads the encrypted chunk through the session, records the ETag/part number, then rewinds the encrypted buffer and submits it for ordered hashing. `submitForHashing` feeds chunks to the session hash only when all prior chunks have been processed; out-of-order chunks are held in `pendingChunks`.

`Close` fails if pending hash buffers remain, sorts completed parts, calls `session.Finish`, then creates Internxt Drive file metadata with AES version `03-aes`, parent directory, original name/ext, size, and modtime. `Abort` closes pending buffers and logs.

## State and Persistence
Remote state includes uploaded encrypted chunks, finalized bucket object, and created Drive metadata. Local state includes part list, pending buffers, ordered hash cursor, and final `meta` consumed by `Object.Update`. Memory use scales with chunk size, upload concurrency, and out-of-order hash backlog.

## Dependencies and Integration Points
Uses Internxt `buckets`, rclone `fs`, `chunksize`, `multipart`, and `pool`. It is invoked by `multipart.UploadMultipart` through `Fs.OpenChunkWriter` in `Object.Update`.

## Risks and Edge Cases
`Abort` logs but does not call a remote abort/delete API, so failed multipart sessions may leave remote temporary state depending on SDK behavior. Hash correctness depends on every encrypted chunk being replayed in byte order; pending buffer leaks are guarded in `Close` but still fatal. Streaming uploads are bounded by max parts times chunk size. Memory pressure can be high for large chunks and concurrent out-of-order completion.

## Test Signals
The integration test config explicitly requires chunked uploads with multiple chunks. There are no local unit tests for ordered hash buffering, chunk-size validation, final metadata creation, or abort cleanup.
