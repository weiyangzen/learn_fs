# sources/user-network-fs/rclone/cmd/mount/mount_test.go

Purpose: runs the generic VFS mount test suite against the bazil `mount` backend.

Important API: `TestMount` calls `vfstest.RunTests(t, false, vfscommon.CacheModeWrites, false, mount)`.

Control flow/state: the test harness creates a mounted VFS with write cache mode and exercises filesystem operations through the OS mountpoint. Persistence is test-local but depends on kernel FUSE availability.

Dependencies/integration: `vfstest` supplies broad behavioral coverage and `vfscommon.CacheModeWrites` sets cache policy. Risks include environmental flakiness on hosts without FUSE permissions or kernel support. The file itself is small, but the integration signal is broad for read/write/list/remove behavior.
