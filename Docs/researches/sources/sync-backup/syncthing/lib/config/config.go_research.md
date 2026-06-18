# sources/sync-backup/syncthing/lib/config/config.go

## sources/sync-backup/syncthing/lib/config/config.go

Purpose: Implements the core Syncthing configuration model, default construction, XML/JSON loading, XML writing, preparation, migration application, lookup/update helpers, and low-level normalization utilities.

Important APIs/types/functions: `Configuration`, `Defaults`, and `Ignores` are the root config structures. Public entry points include `New`, `ReadXML`, `ReadJSON`, `WriteXML`, `Copy`, `ProbeFreePorts`, `Device`, `DeviceMap`, `SetDevice(s)`, `Folder`, `FolderMap`, `FolderPasswords`, and `SetFolder(s)`. Internal helpers include `prepare`, `ensureMyDevice`, `prepareDeviceList`, `prepareFolders`, `prepareDevices`, `prepareIgnoredDevices`, `removeDeprecatedProtocols`, `applyMigrations`, duplicate filtering, untrusted-device share filtering, `filterURLSchemePrefix`, `getFreePort`, and tag-copy helpers.

Control flow and state: Loading sets struct defaults, decodes XML or JSON, applies per-item defaults for JSON folder/device arrays, then calls `prepare`. Preparation ensures the local device is present unless the local ID is empty, removes empty or duplicate devices, validates folders for non-empty unique IDs and paths, removes folder-device references to unknown devices, adds the local device to folder shares, prunes ignored devices/folders that are now configured or shared, prepares GUI/options/defaults, strips deprecated KCP protocols, fills nil slices, and finally applies migrations to `CurrentVersion`. The config persists as indented XML plus a trailing newline.

Dependencies and integration: Integrates with `structutil` for defaults/nil filling, `protocol.DeviceID`, `fs` for marker cleanup, `netutil` for address formatting, `sliceutil`, `slog`, and migration functions. `Wrapper` uses this file for every persisted config replacement; connection code consumes prepared listen addresses, devices, folders, bandwidth options, and defaults.

Risks and test signals: Preparation mutates configuration substantially, so ordering is critical: options prepare before migrations is explicitly protected by `TestIssue1750`. Duplicate folders are fatal, duplicate devices are silently pruned, empty folder paths are fatal, deprecated schemes are removed by prefix, and migration globals are protected by a mutex. `config_test.go` covers defaults, legacy XML migration, JSON validation, copy semantics, ignored devices/folders, untrusted shares, URL filtering, and persistence round trips.
