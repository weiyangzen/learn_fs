<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/rc_test.go -->
# sources/user-network-fs/rclone/vfs/rc_test.go

## Purpose
Tests the VFS remote-control registration and selection behavior for core rc endpoints.

## Important APIs, Types, and Functions
`rcNewRun` creates a test VFS and locates an `rc.Call`. Tests include `TestRcGetVFS`, `TestRcForget`, `TestRcRefresh`, `TestRcPollInterval`, `TestRcList`, and `TestRcStats`.

## Control Flow
Tests set up local-only `fstest` VFS instances, call rc handlers directly, and inspect returned `rc.Params`. `TestRcGetVFS` exercises no-active, implicit single-active, explicit `fs`, wrong `fs`, and ambiguous duplicate-active cases.

## State and Persistence Behavior
The tests create active VFS entries and rely on cleanup to shut them down. `TestRcForget` and `TestRcRefresh` operate on empty/default caches and assert shape of returned results rather than deep cache mutation. `TestRcStats` checks metadata cache counts and options.

## Dependencies and Integration Points
Uses `fs.ConfigString`, `rc.Calls`, `fstest`, `vfscommon.Options`, and the active VFS global registry. Tests skip non-local remotes for determinism.

## Risks and Edge Cases
Several tests contain `FIXME needs more tests`; recursive refresh, path-specific refresh/forget, invalid parameter types, queue endpoints, queue expiry, poll timeout, and unsupported poll interval paths receive little or no coverage here.

## Test Signals
Good signal for `getVFS` compatibility/error behavior and basic rc registration. Limited signal for cache mutation semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/vfs/rc_test.go -->
