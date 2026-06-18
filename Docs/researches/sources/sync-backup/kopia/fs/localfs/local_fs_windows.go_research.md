## sources/sync-backup/kopia/fs/localfs/local_fs_windows.go

Purpose: Windows-specific localfs metadata and path behavior.

Important APIs/types/functions: `isWindows`, `platformSpecificOwnerInfo`, `platformSpecificDeviceInfo`, and `trailingSeparator`.

Control flow, state, and persistence: owner and device metadata return empty values on Windows. `trailingSeparator` detects VSS volume paths under `\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy...` and adds a separator so directory opens and stats can work.

Dependencies and integration points: used by `local_fs_os.go` during `NewEntry` and `Iterate`; supports snapshotting Windows shadow-copy paths that otherwise fail without a trailing slash.

Risks and test signals: risks include missed VSS path variants and lack of Windows owner/device metadata. Localfs tests include Windows-specific split-prefix cases but must run on Windows to validate the VSS behavior.
