# sources/user-network-fs/rclone/vfs/vfstest/vfs.go

## Purpose
Adapts `*vfs.VFS` to the `Oser` interface for direct in-process functional testing.

## APIs, Flow, And State
`vfsOs` embeds `*vfs.VFS` and overrides `Stat` to call `VFS.Stat`, returning `os.FileInfo`. Other methods are inherited from `VFS` methods matching `Oser`.

## Dependencies And Integration
Used when `RunTests` is invoked with `useVFS=true`, such as `vfstest_test.go`. It avoids mounting while exercising the same high-level operations.

## Risks And Test Signals
The adapter is minimal; risk is interface drift if `VFS` methods change. Compile-time assertion confirms `vfsOs` satisfies `Oser`.
