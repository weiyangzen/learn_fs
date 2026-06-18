<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/list.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/list.go

Source read: complete file, 51 lines, 1139 bytes, sha256 `19ff1487f51e40a0aa26328f94c5214c3d34b936cbc3f19a8347da93cbaf62c7`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/list.go_research.md`.

## Purpose
Recursively converts VFS directory entries into a gofakes3 object listing for a bucket and prefix.

## Important APIs, types, and functions
`entryListR` accepts bucket, current directory path, remaining prefix name, delimiter behavior, and the response accumulator.

## Control flow
It stats and reads a directory, filters entries by the remaining prefix component, emits common prefixes when delimiter mode is active, recurses into directories otherwise, and emits content records for files with key, modtime, ETag, size, and storage class.

## State and persistence behavior
No persistent state. It reads VFS directory state and adds to a request-local `ObjectList`.

## Dependencies and integration points
Depends on path helpers, prefix parsing from `utils.go`, `getDirEntries`, ETag hashing, VFS nodes, and `gofakes3` models.

## Risks and edge cases
Filtering is component-based after `prefixParser`; unusual control characters and delimiter semantics are noted by a workaround comment. Recursive listing can be expensive for large buckets.

## Test signals
S3 integration and MinIO client encoding/list tests exercise listing output; `pager_test.go` covers final ordering after listing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/list.go -->
