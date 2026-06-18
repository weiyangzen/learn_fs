# sources/user-network-fs/rclone/cmd/mount2/mount_test.go

Purpose: runs generic VFS mount tests against the go-fuse `mount2` backend.

Important API: `TestMount` calls `vfstest.RunTests(t, false, vfscommon.CacheModeWrites, false, mount)`.

Control flow/state: the shared harness mounts a test filesystem with write caching and executes filesystem operations through the OS mountpoint. It depends on platform build tags (`linux || darwin/amd64`) and FUSE availability.

Dependencies/integration: `vfstest` and `vfscommon`. Risks are environment-specific failures rather than logic in this file. The test is a broad integration signal for `mount2` file, node, and fs adapters.
