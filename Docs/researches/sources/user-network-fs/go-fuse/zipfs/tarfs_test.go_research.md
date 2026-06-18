<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/tarfs_test.go -->
# sources/user-network-fs/go-fuse/zipfs/tarfs_test.go

## Purpose
Tests tar archive filesystem construction and mounted attribute/read behavior.

## Important APIs, Types, and Functions
`TestTar` builds an in-memory tar and mounts `tarRoot`.

## Control Flow
The test writes headers for directory and regular file entries, mounts the resulting tree, lstat checks file types/modes, and reads file contents.

## State and Persistence Behavior
State is an in-memory tar buffer and temp FUSE mount.

## Dependencies and Integration Points
Depends on `archive/tar`, `fs.Mount`, and `HeaderToFileInfo` behavior.

## Risks and Edge Cases
The current fixture map does not include a symlink entry despite code paths checking for one, leaving symlink handling less covered.

## Test Signals
`go test ./zipfs -run TestTar` validates tar tree construction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/tarfs_test.go -->
