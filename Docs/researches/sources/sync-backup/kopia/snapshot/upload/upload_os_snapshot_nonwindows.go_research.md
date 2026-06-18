# sources/sync-backup/kopia/snapshot/upload/upload_os_snapshot_nonwindows.go

## Purpose
Provides non-Windows stubs for OS filesystem snapshot support.

## Important APIs, Types, and Functions
`osSnapshotMode` always returns `policy.OSSnapshotNever`. `createOSSnapshot` returns a "not supported on this platform" error.

## Control Flow
Because mode is always `Never`, normal non-Windows uploads do not call `createOSSnapshot` through the OS snapshot branch. The error remains available if called directly.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Selected by `//go:build !windows`. Paired with `upload_os_snapshot_windows.go` and called by `uploadDirWithCheckpointing`.

## Risks
Non-Windows policies requesting OS snapshots are effectively ignored because mode is forced to `Never`. This is intentional platform gating but means policy behavior differs by build target.

## Test Signals
Upload logging tests explicitly set VolumeShadowCopy to never for predictable behavior. Platform-specific Windows tests would be needed to cover the active implementation.
