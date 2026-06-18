<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/multipart_test.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/multipart_test.go

Source read: complete file, 198 lines, 6949 bytes, sha256 `db6f2165f76840453379787649c0341d49e540889f9a8081359703bf8dcfd5fe`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/multipart_test.go_research.md`.

## Purpose
Tests streamed and fallback multipart upload behavior for serve s3 using MinIO's low-level multipart API.

## Important APIs, types, and functions
`newMultipartTestServer`, `readObject`, and `multipartUploadParts` set up local-backed servers and helpers. Tests cover non-uniform parts, out-of-order concurrent uploads, gaps, and aborts.

## Control flow
Each test starts a temporary local Fs, creates a bucket, starts an S3 server, uses `minio.Core` to create/upload/complete/abort multipart uploads, then reads the backing Fs directly.

## State and persistence behavior
State is temporary local object data plus live in-memory multipart state inside the server. Cleanup shuts down the server and client.

## Dependencies and integration points
Depends on MinIO client, rclone local backend/fstest, random data, proxy defaults, and VFS options.

## Risks and edge cases
Local backend tests PutStream behavior available through rclone features; they do not cover every cloud backend's PutStream edge cases. Concurrency test uses one shuffle order.

## Test signals
Strong signal for streaming assembly correctness, ETag validation path, invalid part gaps, and abort leaving no object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/multipart_test.go -->
