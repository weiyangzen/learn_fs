<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/sighup_unsupported.go -->
# sources/user-network-fs/rclone/vfs/sighup_unsupported.go

## Purpose
Provides a no-op SIGHUP notification implementation for Plan 9 and JavaScript/WASM builds where Unix SIGHUP is unavailable.

## Important APIs, Types, and Functions
Defines the same `NotifyOnSigHup(sighupChan chan os.Signal)` API as `sighup.go`, selected by build tags `plan9 || js`.

## Control Flow
The function intentionally does nothing, allowing `VFS.signalHandler` to wait only for context cancellation on unsupported platforms.

## State and Persistence Behavior
No state and no persistence.

## Dependencies and Integration Points
Imports only `os` for the channel type. Integrates with `vfs.go` through build-tag polymorphism.

## Risks and Edge Cases
On unsupported platforms, users cannot trigger directory-cache flush through SIGHUP. The goroutine still exists but receives no signal events.

## Test Signals
No direct tests. Build tag coverage is expected from platform compilation rather than runtime tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/sighup_unsupported.go -->
