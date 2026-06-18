# Research: sources/sync-backup/syncthing/lib/versioner/util.go

## sources/sync-backup/syncthing/lib/versioner/util.go

Purpose: contains shared versioner mechanics: filename tagging, version discovery, archival, restoration, version filesystem resolution, and cleanup support.

Important APIs/types/functions: exported `ErrDirectory`, `DefaultPath`, `TagFilename`, `UntagFilename`; package helpers `retrieveVersions`, `archiveFile`, `dupDirTree`, `restoreFile`, `versionerFsFromFolderCfg`, `findAllVersions`, `clean`, and `cleanVersions`. `fileTagger` abstracts tagged versus untagged version naming.

Control flow: `archiveFile` checks source existence, rejects symlinks by panic, ensures destination root, duplicates directory tree permissions, then `RenameOrCopy`s a source file to the version filesystem and fixes mtime. `restoreFile` archives or removes anything currently at the restore path, locates either tagged or untagged source versions, then moves it back. `clean` walks version storage, groups tagged versions by original filename, applies a retention callback, and removes empty directories via `emptyDirTracker`.

State and persistence: all persistent state is version files and mtimes. Version identity uses `TimeFormat` tags for most versioners and mtime for trashcan-style untagged files.

Dependencies and integration: uses Syncthing filesystem abstractions, `osutil.RenameOrCopy`, path normalization, config filesystem types, and structured logging. Risks include local timezone parsing, second-level time truncation, symlink assumptions, and permission propagation across different filesystem backends. Tests in adjacent versioner packages and trashcan tests exercise restore and cleanup paths.
