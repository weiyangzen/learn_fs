# sources/sync-backup/restic/internal/fs/vss_windows.go

Purpose: Low-level Windows VSS COM bindings and snapshot lifecycle implementation.

Important APIs: `HRESULT`, VSS constants, `vssError`, `IVssBackupComponents` methods, `IVSSAsync`, `IVSSAdmin`, `IVssEnumObject`, `mountPoint`, `vssSnapshot`, `initializeVssCOMInterface`, `HasSufficientPrivilegesForVSS`, `getVolumeNameForVolumeMountPoint`, `newVssSnapshot`, `Delete`, `getProviderID`, `callAsyncFunctionAndWait`, `loadIVssBackupComponentsConstructor`, `queryInterface`, `isRunningOn64BitWindows`, and `enumerateMountedFolders`.

Control flow and state: Initializes COM and security, creates `IVssBackupComponents`, resolves provider, initializes backup state, gathers metadata, checks volume support, retries snapshot-set creation while another set is in progress, adds the main volume and selected mount points, prepares and creates snapshots asynchronously before returning snapshot device objects. Deletion frees snapshot properties, calls `BackupComplete`, deletes snapshots, and releases COM interfaces.

Dependencies and integration: Used by `LocalVss.snapshotPath`. Depends on `go-ole`, `VssApi.dll`, Windows COM/syscalls, and architecture-specific syscall argument layouts.

Risks: Very high-risk integration surface: unsafe vtable calls, COM initialization rules, admin/backup privileges, timeout/deadline handling, architecture mismatch checks, mount-point partial snapshot behavior, and cleanup after failed `PrepareForBackup`/`DoSnapshotSet`.

Test signals: `fs_local_vss_test.go` validates provider lookup, privilege availability, and live snapshot access when admin privileges are available.
