# sources/sync-backup/kopia/snapshot/upload/upload_os_snapshot_windows.go

## Purpose
Implements Windows Volume Shadow Copy integration for snapshot uploads.

## Important APIs, Types, and Functions
`osSnapshotMode` reads `policy.OSSnapshotPolicy.VolumeShadowCopy.Enable`. `createOSSnapshot` validates local filesystem roots, detects existing shadow copies, creates a VSS snapshot with retry for "another operation in progress", opens the shadow-copy device path as `localfs.Directory`, and returns cleanup that removes the VSS snapshot.

## Control Flow
The uploader asks for mode, then calls `createOSSnapshot` for `Always` or `WhenAvailable`. Creation splits the local path into volume and relative path, creates or reuses a shadow copy, maps the original path into `sc.DeviceObject`, and defers removal unless setup failed.

## State and Persistence Behavior
Creates external OS VSS state and removes it in cleanup. Repository persistence is indirect: upload reads from the shadow-copy directory rather than the live path.

## Dependencies and Integration Points
Windows-only file using `github.com/mxk/go-vss`, `localfs`, `clock.SleepInterruptibly`, and uploader logging. Integrated by `uploadDirWithCheckpointing`.

## Risks
VSS creation/removal is external and can fail due to permissions, concurrent VSS operations, or non-local paths. Retry uses randomized delay. Cleanup logs but does not propagate removal failures. If `WhenAvailable` is configured, creation errors are downgraded by the caller.

## Test Signals
No direct tests in this subset. Practical coverage requires Windows integration tests for local paths, existing shadow copy paths, retryable VSS error 9, cancellation during retry, and cleanup failure logging.
