# sources/user-network-fs/rclone/lib/multipart/multipart.go

Source read signal: reviewed complete local file (130 lines, sha256 582f42d1d8153b81).

Purpose: Implements generic concurrent multipart upload orchestration for backends that expose `fs.OpenChunkWriter`.

Important APIs/types/functions: Exports `BufferSize`, `NewRW`, `UploadMultipartOptions`, and `UploadMultipart`.

Control flow: `UploadMultipart` opens a chunk writer, bounds concurrency with `pacer.TokenDispenser`, creates a cancellable context and abort-on-error hook, unwraps accounting from the input, then loops reading `ChunkSize` buffers from the pool. Each chunk is uploaded in an errgroup goroutine via `WriteChunk`; tokens and buffers are released after upload. After all chunks succeed, it closes/finalizes the chunk writer and returns it.

State and persistence behavior: Uploads remote multipart state through the backend writer. On errors it cancels and, unless configured to leave parts, calls `Abort`.

Dependencies and integration points: Uses `fs.OpenChunkWriter`, `fs.ChunkWriter`, `pool.RW`, `pacer`, `accounting`, `atexit.OnError`, and `errgroup`. It is a backend utility for parallel chunked uploads.

Risks and test signals: Correctness depends on chunk writer concurrency safety and respecting cancellation. The first empty object still uploads one zero-length chunk only when `io.CopyN` returns EOF with part zero. Abort/finalize behavior needs backend integration tests.
