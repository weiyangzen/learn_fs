<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_linux_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_linux_test.go

## Purpose

This Linux-specific mounting test verifies `statfs` values exposed by a mounted canned gcsfuse filesystem on Linux.

## Important APIs, Types, and Functions

`GcsfuseTest.Statfs` mounts the canned bucket, calls `syscall.Statfs`, and checks `Frsize`, `Blocks`, `Bfree`, `Bavail`, `Files`, `Ffree`, and `Bsize`.

## Control Flow

The test mounts `canned.FakeBucketName`, defers unmount, calls `syscall.Statfs`, asserts fragment size is non-zero, checks byte-capacity multiplication cannot overflow and represents at least 1 TiB, validates all blocks are free/available, validates a large free inode count, and expects block size/recommended IO size of 1 MiB.

## State and Persistence Behavior

State is only the temporary mount and kernel statfs response. It does not write to the filesystem.

## Dependencies and Integration Points

It depends on the shared `GcsfuseTest` harness, Linux syscall layout, canned bucket, and unmount utility. It complements the Darwin-specific statfs file.

## Risks and Test Signals

Any change to advertised capacity, inode, or block size policy will break assertions. Passing signal is a Linux FUSE mount with sane capacity and IO-size metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_linux_test.go -->
