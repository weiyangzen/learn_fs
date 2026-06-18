<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/pager.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/pager.go

Source read: complete file, 66 lines, 1530 bytes, sha256 `b0c8be0152760c30cd641b2ff0ca2a5bef9eb5b5200a8effe890d04f068e4654`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/pager.go_research.md`.

## Purpose
Implements S3 list pagination and deterministic ordering for gofakes3 object lists.

## Important APIs, types, and functions
`pager` sorts common prefixes and object contents lexicographically, applies marker trimming, fills a response up to MaxKeys, marks truncation, and sets NextMarker.

## Control flow
ListBucket builds a full `ObjectList` first, then calls this function to page it according to gofakes3's `ListBucketPage`.

## State and persistence behavior
No persistent state; it mutates the passed list slices and returns a new response list.

## Dependencies and integration points
Depends on Go `sort` and gofakes3 list structures.

## Risks and edge cases
The truncation check compares original remaining list length to `page.MaxKeys`; when `MaxKeys` is zero, tokens default to 1000 but the check still uses zero, which can mark truncated unexpectedly. Marker handling treats contents and prefixes independently.

## Test signals
`pager_test.go` verifies content sorting by key.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/pager.go -->
