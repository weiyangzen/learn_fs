# sources/user-network-fs/rclone/backend/pikpak/multipart.go

Purpose: implements PikPak resumable multipart uploads using AWS S3 SDK calls against credentials returned by PikPak.

Important APIs/types/functions: `getPool` and `NewRW` manage pooled upload buffers. `pikpakChunkWriter` tracks chunk size, file size, concurrency, source reader, completed parts, S3 client, and multipart upload output. `newChunkWriter` creates an S3 client, calculates chunk size, applies upload headers, and starts multipart upload. `Upload`, `WriteChunk`, `Abort`, and `Close` perform concurrent part upload and finalization.

Control flow: `Upload` uses a token dispenser for concurrency, reads source chunks into pooled `pool.RW` buffers, and uploads each chunk through an errgroup. On error, an `atexit.OnError` callback cancels the context and aborts the multipart upload. `WriteChunk` seeks to determine part size, rewinds, uploads the S3 part, and records ETag/part number. `Close` sorts completed parts before `CompleteMultipartUpload`.

State and persistence: local transient state includes buffers, tokens, completed part slice, and upload ID. Remote state is the in-progress multipart object. Abort is best-effort.

Dependencies/integration: depends on AWS SDK v2 S3, rclone accounting, chunksize, pacer, pool, atexit, and `api.ResumableParams`. Called from `Fs.uploadByResumable`.

Risks/test signals: memory scales with transfers times upload concurrency times chunk size. Unknown-size streaming is bounded by chunk size times 10,000 parts. Abort failures are logged but not recovered. Integration tests configure chunk size limits and exercise this path indirectly.
