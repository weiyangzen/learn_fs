# sources/user-network-fs/rclone/backend/drive/upload.go

## Purpose
`upload.go` implements Drive resumable uploads for large or unknown-size objects. It starts a resumable upload session, sends data in configured chunks, retries each chunk through the backend pacer, and returns the final Drive `File` metadata.

## Important APIs, types, and functions
- `statusResumeIncomplete` is HTTP 308, the Drive resumable-upload in-progress response.
- `resumableUpload` stores the owning `Fs`, remote name for logging, session URI, media reader, content type, total length, and final returned `drive.File`.
- `Fs.Upload` starts a Drive upload session using POST for creates or PATCH for updates, sets upload metadata headers, handles `keepRevisionForever`, and then calls `resumableUpload.Upload`.
- `makeRequest` builds a chunk request with `Content-Range` using either known total size or `*` for initially unknown total size.
- `transferChunk` sends a chunk, handles 308 as nonterminal, checks non-308 responses, and decodes the final response body.
- `resumableUpload.Upload` reads chunks from the input, uses repeatable readers for known-size transfers and buffer reads for unknown-size transfers, retries through `pacer.Call`, and reports incomplete sessions as retryable.

## Control flow
The caller passes object metadata and content to `Fs.Upload`. A resumable session is created against `https://www.googleapis.com/upload/drive/v3/files` with `uploadType=resumable`; update calls expand `{fileId}` and use PATCH. Once Google returns a `Location`, `resumableUpload.Upload` loops from offset zero, preparing a chunk no larger than `opt.ChunkSize`. Known-size uploads stop when `start >= ContentLength`; unknown-size uploads read until EOF, then set `ContentLength` to the final byte count so the last `Content-Range` closes the upload. Each chunk is retried unless the status is 308, 201, or 200. The final response is decoded into `rx.ret`.

## State and persistence behavior
The upload persists file contents and metadata to Google Drive. Locally, only the resumable session URI, current offset, chunk buffer, and final returned metadata are held. The configured chunk size controls memory usage because one buffer of that size is allocated per upload instance.

## Dependencies and integration points
This file depends on `drive.go` for `Fs`, `partialFields`, `shouldRetry`, `opt.ChunkSize`, `opt.KeepRevisionForever`, and the authorized HTTP client. It uses rclone reader helpers for repeatable and fill reads, Google API response helpers, and `fserrors.RetryErrorf` so higher layers can restart incomplete sessions.

## Risks and edge cases
- The session start request is retried, but simple media create/update elsewhere deliberately uses no-retry behavior; callers must choose the correct path.
- Unknown-size uploads depend on EOF handling to send a final chunk with a concrete total length.
- If `rx.ret` remains nil after all chunks, the function returns a retryable incomplete-upload error.
- Chunks require repeatable readers for retry; known-size mode uses `NewRepeatableLimitReaderBuffer`, while unknown-size mode buffers each chunk in memory.
- Nonstandard local status codes 598/599 are used internally for decode/client errors.

## Test signals
`drive_test.go` configures generic chunked upload integration tests with Drive's minimum chunk size and power-of-two sizing. The main integration suite exercises this uploader whenever object size meets or exceeds `UploadCutoff` or size is unknown.
