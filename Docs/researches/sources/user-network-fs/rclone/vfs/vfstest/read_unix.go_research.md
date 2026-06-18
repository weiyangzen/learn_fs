# sources/user-network-fs/rclone/vfs/vfstest/read_unix.go

## Purpose
Tests mounted read handles when file descriptors are duplicated and closed in different orders.

## APIs, Flow, And State
`TestReadFileDoubleClose` opens a file, duplicates the fd twice, closes one duplicate, reads through the original, closes it, reads through the remaining duplicate, then closes that duplicate. It verifies no input/output error after buffered read paths.

## Dependencies And Integration
Unix build-tagged for Linux, Darwin, and FreeBSD. Uses raw `syscall.Dup`, `Close`, and `Read`, and skips direct VFS mode because it needs kernel fd behavior.

## Risks And Test Signals
Detects FUSE/mount implementations that mishandle flush/release on duplicated read descriptors. It is platform-specific and depends on mounted semantics.
