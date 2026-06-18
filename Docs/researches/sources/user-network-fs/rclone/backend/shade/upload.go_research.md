# sources/user-network-fs/rclone/backend/shade/upload.go

Purpose: implements Shade multipart uploads via rclone's `fs.OpenChunkWriter` / `multipart.UploadMultipart` infrastructure.

Important APIs/types/functions: `shadeChunkWriter` stores the upload token, chunk size, source size, backend/object pointers, and completed parts guarded by a mutex. `Object.uploadMultipart` delegates to generic multipart upload. `Fs.OpenChunkWriter` computes chunk sizing, ensures parents, initiates multipart upload, and returns writer metadata. `WriteChunk` reads a chunk, fetches a presigned part URL, PUTs the bytes, records ETag/part number, and returns bytes written. `Close` sorts parts and completes the upload. `Abort` asks Shade to abort the multipart token. `warnStreamUpload` logs the unknown-size upload ceiling once.

Control flow: for known sizes, `chunksize.Calculator` adjusts part size to stay under max parts; for unknown sizes, configured chunk size is used. Each part obtains a fresh JWT, then a part URL, then uploads to that URL with any returned headers. Completion sends sorted parts to the complete endpoint; abort deliberately avoids retrying failures.

State and persistence behavior: multipart state is remote via the init token and local via `completedParts`. The writer updates `Object.size` from the writer's source size after upload. No resumable local state is stored.

Dependencies/integration: uses rclone `multipart`, `chunksize`, `rest`, Shade API DTOs, and the backend token/directory helpers. Exposed through `Fs.Features().OpenChunkWriter`.

Risks/test signals: memory use is one full chunk per concurrent upload because chunks are buffered; unknown-size uploads are capped by chunk size times max parts; ETag presence and JSON field names must match service expectations; error message for failed upload formats the chunk buffer instead of part number. Integration tests are the main coverage.
