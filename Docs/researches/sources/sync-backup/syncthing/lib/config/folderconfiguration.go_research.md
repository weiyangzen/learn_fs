# sources/sync-backup/syncthing/lib/config/folderconfiguration.go

## sources/sync-backup/syncthing/lib/config/folderconfiguration.go

Purpose: Defines folder-level configuration, filesystem construction, marker management, path health checks, preparation rules, restart filtering, free-space checks, and extended-attribute filters.

Important APIs/types/functions: Key types are `FolderConfiguration`, `FolderDeviceConfiguration`, `XattrFilter`, and `XattrFilterEntry`. Important methods include `Copy`, `Filesystem`, `ModTimeWindow`, `CreateMarker`, `RemoveMarker`, `CheckPath`, `CreateRoot`, `Description`, `LogAttr`, `DeviceIDs`, `prepare`, `RequiresRestartOnly`, `Device`, `SharedWith`, `CheckAvailableSpace`, `XattrFilter.Permit`, and XML/JSON unmarshal methods that set defaults.

Control flow and state: `Filesystem` builds an `fs.Filesystem` with options for junction handling and case-conflict detection. Marker creation validates the path first, creates `.stfolder` plus a hashed marker file, syncs the root, and hides the marker. Preparation removes invalid/duplicate device shares, ensures the local device is shared, removes untrusted devices from trusted shares, sorts devices, clamps rescan and version cleanup intervals, normalizes watcher delay, defaults marker name and max concurrent writes, and forces `IgnorePerms` for receive-encrypted folders.

Dependencies and integration: Integrates with `lib/fs`, `protocol`, `build`, `disk.Usage` on Android, `structutil`, logging, and helpers in `config.go`. Puller/scanner/model code consumes these settings for filesystem access, scheduling, xattrs, versioning, and safety checks.

Risks and test signals: Marker and free-space checks guard data loss; untrusted-device filtering is security-sensitive; path validation rejects missing marker/root cases distinctly. Tests cover path health, large interval clamping, receive-encrypted ignore permissions, xattr filter semantics, versioning serialization, untrusted shares, and empty path rejection.
