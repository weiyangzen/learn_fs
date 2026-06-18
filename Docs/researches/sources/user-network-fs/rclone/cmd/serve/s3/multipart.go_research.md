<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/multipart.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/multipart.go

Source read: complete file, 388 lines, 11768 bytes, sha256 `6fad721d67310ea5d287be916c34b01fda5b5095d4aaa87123b540bf4e3acb5d`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/multipart.go_research.md`.

## Purpose
Implements streaming S3 multipart uploads so completed objects can be written to backends via `PutStream` without buffering the entire upload in memory.

## Important APIs, types, and functions
`multipartUpload` tracks bucket/key, metadata, pipe writer, MD5s, part sizes, stream buffer, next part, and background PutStream lifecycle. `CreateMultipartUpload`, `UploadPart`, `CompleteMultipartUpload`, `AbortMultipartUpload`, `validate`, `streamPart`, `close`, `abort`, and `multipartETag` implement `gofakes3.MultipartBackend`.

## Control flow
Creation validates bucket and PutStream support, creates parent directories, starts a background `PutStream` reading from an `io.Pipe`, and stores upload state. Each part is copied into a pool-backed buffer while MD5 is computed; the part is streamed when all earlier parts have arrived. Complete validates client ETags/order, ensures contiguous streaming, closes the pipe, invalidates VFS parent cache, stores metadata, applies mtime, and returns the S3 multipart ETag.

## State and persistence behavior
Remote object data is streamed to the underlying Fs before completion. Local upload state is held in `multipartUploads` until complete or abort. Buffered out-of-order parts consume pool storage until their turn. Abort cancels context and closes the pipe with a sentinel error.

## Dependencies and integration points
Depends on `gofakes3`, `uuid`, `fs.Features().PutStream`, `object.NewStaticObjectInfo`, `lib/multipart`, `pool.RW`, Swift mtime helpers, and VFS cache invalidation.

## Risks and edge cases
Requires part numbers to become contiguous; gaps are rejected at completion. Out-of-order clients are tolerated only within memory/disk buffer limits. PutStream bypasses VFS, so parent cache invalidation is essential. Fallback to gofakes3 in-memory buffering can use large memory and is logged once.

## Test signals
`multipart_test.go` covers non-uniform parts, in-memory fallback, concurrent out-of-order parts, non-contiguous rejection, and abort cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/multipart.go -->
