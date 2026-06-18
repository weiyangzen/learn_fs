# sources/sync-backup/syncthing/lib/config/observed.go

## sources/sync-backup/syncthing/lib/config/observed.go

Purpose: Defines persisted observations of remote devices and folders that were ignored or pending historically.

Important APIs/types/functions: `ObservedFolder` stores time, folder ID, and label. `ObservedDevice` stores time, device ID, name, and address.

Control flow and state: Pure data structures with JSON/XML tags. They are persisted under device ignored folders and root ignored devices.

Dependencies and integration: Depends on `time.Time` and `protocol.DeviceID`. Used by `DeviceConfiguration.IgnoredFolders`, `Configuration.IgnoredDevices`, and deprecated pending fields.

Risks and test signals: Stale observed entries must be pruned when the device/folder is configured or shared. Tests `TestIgnoredDevices`, `TestIgnoredFolders`, and `TestIssue4219` validate that behavior.
