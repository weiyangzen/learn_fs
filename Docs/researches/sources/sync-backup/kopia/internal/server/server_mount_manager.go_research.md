<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_mount_manager.go -->
# sources/sync-backup/kopia/internal/server/server_mount_manager.go

- Purpose: Manages active snapshot mount controllers keyed by root object ID.
- Important APIs/types/functions: `getMountController`, `listMounts`, `deleteMount`, `unmountAllLocked`.
- Control flow: `getMountController` checks the `Server.mounts` map under `serverMutex`, returns an existing controller, optionally creates a new `mount.Directory` over `snapshotfs.DirectoryEntry`, and stores it. Listing clones the map; delete/unmount remove entries.
- State and persistence: State is in-memory only in `Server.mounts`; mounted filesystem state is owned by the mount controller.
- Dependencies and integration points: Integrates `internal/mount`, `snapshot/snapshotfs`, repository object IDs, and server HTTP mount routes elsewhere.
- Risks and edge cases: `unmountAllLocked` requires the caller already hold `serverMutex`; unmount failures are logged but entries are still deleted.
- Test signals: No direct test in this file; mount behavior is indirectly exercised through server API tests and mount controller implementations.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/server/server_mount_manager.go -->
