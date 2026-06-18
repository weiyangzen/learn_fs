# sources/sync-backup/kopia/snapshot/snapshotfs/repofs.go

Purpose: implements a virtual filesystem over Kopia repository snapshot objects.

Important APIs/types/functions: `repositoryEntry`, `repositoryDirectory`, `repositoryFile`, `repositorySymlink`, `EntryFromDirEntry`, `DirectoryEntry`, `SnapshotRoot`, `AutoDetectEntryFromObjectID`, `IsDirectoryID`, and `withFileInfo`.

Control flow: directory contents are lazily loaded from repository objects through `readDirEntries` under a mutex and cached by name. Files open object readers. Symlinks read their target object. Auto-detection treats IDs with directory content prefix as possible directories and falls back to synthetic files.

State and persistence: read-only repository access with per-directory cached entries/summary that can be dropped by `Close`. It mutates loaded directory child metadata to reflect summary size and max mod time for directories.

Dependencies and integration points: core adapter used by restore, tree walking, verification, object reference resolution, mounts, and storage stats.

Risks and test signals: `Resolve` for symlinks is not implemented. Directory autodetection opens and iterates objects, so corrupt directory-looking objects become files. Unknown entry types become `fs.ErrorEntry`. Tests exercise walker, verifier, source browsing, and storage stats through this adapter.
