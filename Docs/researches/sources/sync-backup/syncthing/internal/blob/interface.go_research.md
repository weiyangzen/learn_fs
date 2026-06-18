# sources/sync-backup/syncthing/internal/blob/interface.go

## Purpose
This file defines the minimal blob storage abstraction used by Syncthing internals that need upload, download, and latest-object lookup without depending on a concrete backend.

## Important APIs, Control Flow, And State
`Store` exposes `Upload(ctx, key, reader)`, `Download(ctx, key, writer)`, and `LatestKey(ctx)`. `Writer` combines `io.Writer` and `io.WriterAt`, matching download APIs that can write chunks at offsets. There is no implementation or state in this file.

## Dependencies And Integration Points
It depends only on `context` and `io`. The S3 implementation in `internal/blob/s3/s3.go` satisfies this interface. Callers can provide any backend with equivalent semantics.

## Risks And Test Signals
The interface does not specify ordering semantics for `LatestKey`, missing-key behavior, overwrite behavior, or whether implementations must honor context cancellation. Implementations should be tested against these behavioral expectations, especially concurrent multipart downloads that require `WriterAt`.
