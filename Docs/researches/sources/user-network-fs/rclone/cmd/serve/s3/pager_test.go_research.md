<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/pager_test.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/pager_test.go

Source read: complete file, 32 lines, 792 bytes, sha256 `ce698a03ed47914093fe12a2034232923b85f0582ad249eb69ef7c4134495794`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/pager_test.go_research.md`.

## Purpose
Tests S3 pager ordering behavior.

## Important APIs, types, and functions
`TestPagerSortsContentsByKey` creates an unsorted object list, calls `pager`, and asserts lexicographic key order.

## Control flow
The test avoids a full server and invokes the backend helper directly.

## State and persistence behavior
No persistent state.

## Dependencies and integration points
Depends on gofakes3 object list models and testing package.

## Risks and edge cases
Coverage is narrow: it does not check prefix ordering, markers, truncation, or zero MaxKeys behavior.

## Test signals
Provides regression signal that returned contents are sorted by key.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/pager_test.go -->
