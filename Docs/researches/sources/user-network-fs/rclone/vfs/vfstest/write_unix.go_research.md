# sources/user-network-fs/rclone/vfs/vfstest/write_unix.go

## Purpose
Tests write behavior with duplicated file descriptors on Unix-like platforms and provides the Unix implementation of `writeTestDup`.

## APIs, Flow, And State
`TestWriteFileDoubleClose` opens a writer, duplicates its fd twice, closes one duplicate, writes through the original, closes it, then writes through the second duplicate. It expects an error below `CacheModeWrites` and success at write-capable cache modes. `writeTestDup` wraps `unix.Dup`.

## Dependencies And Integration
Build-tagged for Linux, Darwin, FreeBSD, and OpenBSD, though Darwin skips the test. Uses `golang.org/x/sys/unix` and VFS cache-mode options.

## Risks And Test Signals
Detects mount-layer mishandling of flush/release with duplicated writer descriptors. Expected behavior depends on cache mode, so it guards both restriction and success paths.
