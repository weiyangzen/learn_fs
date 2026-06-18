# sources/user-network-fs/rclone/vfs/vfstest_test.go

## Purpose
Runs the shared `vfstest` functional suite directly against the in-process VFS implementation.

## APIs, Flow, And State
`TestFunctional` skips non-local remotes, then calls `vfstest.RunTests` with `useVFS=true`, minimum cache mode off, cache tests enabled, and a dummy `mountFn` that returns an immediately successful unmount channel.

## Dependencies And Integration
Imports all backends, `fstest`, `mountlib`, `vfs`, `vfscommon`, and `vfstest`. This is the direct-VFS entry point for the broader functional tests.

## Risks And Test Signals
It avoids real mount behavior, so kernel/FUSE-specific bugs are not covered here. It gives broad signal for in-process VFS semantics across cache modes and writeback/link variants on local remotes.
