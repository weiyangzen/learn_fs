<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount_test.go -->
# sources/user-network-fs/rclone/cmd/cmount/mount_test.go

## Purpose

`mount_test.go` runs the standard VFS mount test suite against the cmount implementation.

## Important APIs, Types, and Functions

`TestMount` skips unreliable macOS runs, then calls `vfstest.RunTests(t, false, vfscommon.CacheModeOff, true, mount)`. The build tags exclude unsupported cmount targets and Windows race-detector builds.

## Control Flow

The test delegates all behavioral scenarios to `vfstest`, using the package `mount` function as the mount backend under test.

## State and Persistence Behavior

Tests create temporary remotes and live mounts, then rely on the VFS test harness for cleanup.

## Dependencies and Integration Points

It integrates with `fstest/testy`, `vfstest`, `vfscommon`, and build-tag platform selection.

## Risks and Test Signals

Risk is weak local coverage when platform tests are skipped or flaky. Signals include successful VFS read/write/list/delete flows, cache-mode-off behavior, mount/unmount cleanup, and race-detector exclusions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount_test.go -->
