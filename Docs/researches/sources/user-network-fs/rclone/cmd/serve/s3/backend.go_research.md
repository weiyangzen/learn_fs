<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/backend.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/backend.go

Source read: complete file, 529 lines, 12864 bytes, sha256 `966d757df7f60c42eda1b934dc942381f6eec85771e0f4345606cc5aa3bbf705`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/backend.go_research.md`.

## Purpose
Implements the `gofakes3.Backend` bridge from S3 buckets/objects to rclone VFS paths and optional streaming multipart support.

## Important APIs, types, and functions
`s3Backend` stores the server pointer, metadata map, multipart upload registry, and fallback warning guard. It implements bucket listing/creation/deletion, object head/get/put/touch/copy/delete, multi-delete, bucket existence, and metadata/modtime helpers.

## Control flow
Bucket operations map top-level VFS directories to buckets. Object operations join bucket and key into a VFS path, stat/open/create/remove VFS nodes, copy data streams, and convert hashes/modtimes/mime types into S3 metadata. Copy to self updates metadata/modtime; copy to another key reads the source and writes via `PutObject`.

## State and persistence behavior
Remote state is directories and files in the backing Fs through VFS. Local state is an in-memory metadata map keyed by full path and multipart upload state held in `multipartUploads`. Metadata is not persisted across process restarts.

## Dependencies and integration points
Depends on `gofakes3`, rclone VFS, `fs.Object`, Swift float-time helpers for mtime metadata, and helper files `utils.go`, `list.go`, `ioutils.go`, and `multipart.go`.

## Risks and edge cases
The metadata map can diverge from remote state after external changes. Directory cleanup after delete is marked unsafe and may remove empty parents unexpectedly. `PutObject` has nuanced mtime handling where fallback to `mtime` is nested under `X-Amz-Meta-Mtime` parsing. Root files are not represented as buckets.

## Test signals
`s3_test.go` runs backend integration through the S3 backend, encoding tests, auth/proxy bucket listing, and rc tests. Multipart behavior is covered separately.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/backend.go -->
