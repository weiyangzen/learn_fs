# sources/sync-backup/syncthing/lib/config/filesystemtype.go

## sources/sync-backup/syncthing/lib/config/filesystemtype.go

Purpose: Defines configuration-level filesystem type names and maps them to `lib/fs` filesystem types.

Important APIs/types/functions: `FilesystemType` string enum has `basic` and `fake`; methods are `ToFS`, `String`, `MarshalText`, `UnmarshalText`, and `ParseDefault`.

Control flow and state: Empty string is treated as `basic` for legacy compatibility in all conversion paths. Unknown non-empty strings pass through to `fs.FilesystemType`, allowing extension by the filesystem layer.

Dependencies and integration: Used by `FolderConfiguration.FilesystemType` and `VersioningConfiguration.FSType`; `FolderConfiguration.Filesystem` calls `ToFS`.

Risks and test signals: Pass-through unknown values can be useful for extensions but may fail later when creating a filesystem. Historical fixtures and folder path tests exercise legacy empty/basic behavior indirectly.
