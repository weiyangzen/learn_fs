# sources/user-network-fs/go-fuse/fs/loopback_linux_test.go

Purpose: Linux-specific loopback integration tests for rename flags, xattrs, copy_file_range, mount races, direct/id options, ioctl passthrough, and mknod.

Important tests/functions: `TestRenameNoOverwrite`, `TestRenameWhiteOut`, `TestXAttrSymlink`, `TestCopyFileRange`, `waitMount` helpers for `/proc/self/mounts`, `TestParallelDiropsHang`, `TestRoMount`, `TestDirectMount`, `TestIoctlLoopbackFile`, `TestIoctlLoopbackDir`, and `TestMknod`.

State/dependencies: real backing dirs and FUSE mounts; Linux syscalls `Renameat2`, `CopyFileRange`, ioctl flags, `/proc`, `/sys/class/bdi`, and sometimes root/direct mount capability.

Risks/test signals: strong coverage of Linux-specific kernel integration. Environment sensitivity is high: kernel version, permissions, filesystem support for noatime/xattrs, and FUSE capabilities can affect results.
