<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/zipfs_test.go -->
# sources/user-network-fs/go-fuse/zipfs/zipfs_test.go

## Purpose
Tests zip archive filesystem mounting, attributes, content reads, and link count reporting.

## Important APIs, Types, and Functions
`testZipFile`, `setupZipfs`, `TestZipFs`, and `TestLinkCount` are the test helpers/cases.

## Control Flow
The setup locates `test.zip`, builds an archive filesystem, mounts it, and tests root entries, directory type, file mode, block count, mtime, content, and Nlink.

## State and Persistence Behavior
State is a temp FUSE mount over a static test archive.

## Dependencies and Integration Points
Depends on runtime caller path discovery, FUSE support, and `zipfs.go`.

## Risks and Edge Cases
The setup ignores mount errors before returning cleanup, which could panic if mount failed. Tests assume exact metadata in the fixture archive.

## Test Signals
`go test ./zipfs` is the main signal for zipfs behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/zipfs_test.go -->
