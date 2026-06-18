<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/s3_test.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/s3_test.go

Source read: complete file, 316 lines, 7935 bytes, sha256 `597dd1c9ea1189e2878b0fcf9a4f5de6da0ecd84b90a4c43af74e47c3cdbcb7a`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/s3_test.go_research.md`.

## Purpose
Runs serve s3 integration tests and MinIO-client behavior checks.

## Important APIs, types, and functions
`serveS3` and `startS3` start an authenticated local S3 server and return backend config. `TestS3`, `TestS3Minio`, `TestEncodingWithMinioClient`, and bucket-list/auth helper tests exercise normal and auth-proxy modes.

## Control flow
Tests launch serve s3, configure rclone's S3 backend or MinIO client to talk to it, then run generic backend tests or explicit list operations.

## State and persistence behavior
State is temporary local or Docker-backed remote content plus live server listeners. Proxy tests temporarily mutate global `proxy.Opt.AuthProxy`.

## Dependencies and integration points
Depends on MinIO client, rclone S3 backend, local backend, servetest, fstest, docker-backed testserver for MinIO, hashes, random credentials, and rc.

## Risks and edge cases
Docker-backed coverage is skipped without Docker. Global proxy option mutation is not parallel-safe. Integration failures can come from the nested backend tests rather than the S3 server alone.

## Test signals
Broad conformance signal for serving S3 over local and MinIO-backed remotes, path encoding, auth keys, auth proxy, and rc startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/s3_test.go -->
