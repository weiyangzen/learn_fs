# sources/sync-backup/syncthing/lib/config/versioningconfiguration.go

## sources/sync-backup/syncthing/lib/config/versioningconfiguration.go

Purpose: Defines folder versioning configuration and custom XML/JSON handling for map-like parameters.

Important APIs/types/functions: `VersioningConfiguration` stores type, params map, cleanup interval, filesystem path, and filesystem type. Internal XML types are `internalVersioningConfiguration` and `internalParam`. Methods include `Reset`, `Copy`, `UnmarshalJSON`, `UnmarshalXML`, `MarshalXML`, `toInternal`, and `fromInternal`.

Control flow and state: JSON unmarshal applies defaults before decoding. XML unmarshal decodes to an internal slice representation, then builds `Params`. XML marshal converts the map to sorted `param` elements so output is deterministic.

Dependencies and integration: Uses `structutil`, `FilesystemType`, sorting, and XML/JSON packages. Consumed by `FolderConfiguration.Versioning` and migrations that move legacy params into `FSPath`/`FSType`.

Risks and test signals: Param-map ordering must be deterministic for stable config writes. Tests cover XML serialization and fixture parsing of versioning params.
