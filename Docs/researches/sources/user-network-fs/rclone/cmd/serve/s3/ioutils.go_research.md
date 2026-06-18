<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/ioutils.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/ioutils.go

Source read: complete file, 34 lines, 577 bytes, sha256 `249d1cd61518e27aab35a68ffecea20ffd706f89ed78bc63fbcf48b7806f4d8e`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/ioutils.go_research.md`.

## Purpose
Provides small `io.ReadCloser` utilities for S3 object responses.

## Important APIs, types, and functions
`noOpReadCloser` is an empty body for HEAD-like responses. `readerWithCloser` wraps a reader plus close callback. `limitReadCloser` combines `io.LimitReader` with a closer for ranged reads.

## Control flow
Get/Head object code returns these wrappers to satisfy gofakes3 object body expectations without leaking underlying file handles.

## State and persistence behavior
No persistent state; close callback ownership is passed from the VFS handle.

## Dependencies and integration points
Depends only on `io`.

## Risks and edge cases
Correct close propagation is important for ranged requests because the limited reader itself does not close the underlying file.

## Test signals
Covered indirectly by S3 GET/HEAD and ranged object integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/ioutils.go -->
