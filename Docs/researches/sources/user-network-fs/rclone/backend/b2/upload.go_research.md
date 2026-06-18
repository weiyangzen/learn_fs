# sources/user-network-fs/rclone/backend/b2/upload.go

## Purpose
Implements Backblaze B2 large-file uploads and multipart server-side copies: start/cancel/finish large files, upload/copy parts, track SHA1s, buffer streaming input, control concurrency, and clean up on error.

## Important APIs, types, and functions
`hashAppendingReader` appends the hex digest after source EOF for B2 `hex_digits_at_end` uploads. `largeUpload` tracks parent fs/object, operation type, input/accounting wrapper, large-file ID, size, part count, ordered SHA1s, part upload URLs, chunk size, source object for copy, and final file info. `newLargeUpload` calculates chunk size/parts, starts `/b2_start_large_file`, sends modtime/MIME/custom metadata, optional SHA1 metadata, and SSE-C data. `WriteChunk`, `copyChunk`, `Close`, `Abort`, `Stream`, and `Copy` implement the part lifecycle.

## Control flow
Known-size uploads calculate a chunk size that respects B2's maximum part count. Unknown-size streams use configured chunk size and fail when too many parts are needed. Each part upload obtains a reusable part URL, seeks to determine and rewind size, appends part SHA1 to the body, sends B2 headers, records SHA1, and clears bad upload URLs on retryable errors. `Stream` uploads buffered chunks in an errgroup; `Copy` submits `/b2_copy_part` calls with upload concurrency limits. Both abort on returned error.

## State and persistence
Remote state is the B2 large-file session, uploaded/copied parts, final file version, or cancellation marker. Local state is in-memory buffers, SHA1 slice, upload URL cache, errgroup context, and final response metadata.

## Dependencies and integration points
Called from `Object.Update`, `Fs.copy`, and `OpenChunkWriter` in `b2.go`, and by rclone multipart support through `fs.ChunkWriter`. Uses B2 API types, accounting, chunksize calculator, pool buffers, transfer accounter, pacer/rest, atexit, and errgroup.

## Risks
Part SHA1 ordering must be complete and exact. `WriteChunk` requires seekable readers. Retry correctness depends on rewinding and clearing failed part URLs. Large uploads must be aborted on failure or B2 start markers remain. Memory pressure scales with chunk size and upload concurrency.

## Test signals
Exercised indirectly by B2 generic chunked upload tests and internal metadata/unfinished-upload cleanup tests.
