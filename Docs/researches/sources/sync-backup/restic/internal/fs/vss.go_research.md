# sources/sync-backup/restic/internal/fs/vss.go

Purpose: Non-Windows stubs for VSS types and functions.

Important APIs: `mountPoint`, `vssSnapshot`, `HasSufficientPrivilegesForVSS`, `getVolumeNameForVolumeMountPoint`, `newVssSnapshot`, `Delete`, and `GetSnapshotDeviceObject`.

Control flow and state: All snapshot-related operations either return false/empty values, return the input mount point, or return an error explaining VSS is Windows-only.

Dependencies and integration: Lets `fs_local_vss.go` compile on all platforms while only functioning on Windows.

Risks: Callers must not expect VSS functionality outside Windows; error strings are the operational signal.

Test signals: Windows-specific tests cover real VSS; non-Windows behavior is compile-time compatibility.
