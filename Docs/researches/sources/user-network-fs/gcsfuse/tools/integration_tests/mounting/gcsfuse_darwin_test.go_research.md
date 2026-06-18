<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_darwin_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_darwin_test.go

## Purpose

This Darwin-specific mounting test verifies `statfs` values exposed by a mounted canned gcsfuse filesystem on macOS.

## Important APIs, Types, and Functions

`convertStatfsString` converts NUL-terminated `[]int8` mount source bytes into a Go string. `GcsfuseTest.Statfs` mounts the canned bucket, calls `syscall.Statfs`, and checks block, inode, IO size, and mount source fields.

## Control Flow

The test mounts `canned.FakeBucketName` at the suite temp dir using `runGcsfuse`, defers unmount, then performs `syscall.Statfs`. It verifies available byte calculations do not overflow, total bytes are at least 1 TiB, blocks/free/available are equal, inode count is large and free equals total, IO size is 1 MiB, and the filesystem name matches the fake bucket name.

## State and Persistence Behavior

State is limited to a temporary mount point and kernel statfs data from the mounted FUSE filesystem. No bucket or file mutations are performed.

## Dependencies and Integration Points

It depends on `GcsfuseTest` from `gcsfuse_test.go`, the canned bucket implementation, Darwin `syscall.Statfs_t` fields, and `util.Unmount`.

## Risks and Test Signals

This file is build-target specific and field names differ from Linux. Passing signal is a mounted filesystem reporting reasonable capacity/inode metadata and correct mount source name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_darwin_test.go -->
