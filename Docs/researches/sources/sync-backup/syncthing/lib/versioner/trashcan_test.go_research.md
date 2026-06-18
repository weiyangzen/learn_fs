# Research: sources/sync-backup/syncthing/lib/versioner/trashcan_test.go

## sources/sync-backup/syncthing/lib/versioner/trashcan_test.go

Purpose: exercises trashcan versioning behavior where archived files keep their original names instead of timestamp-tagged names. It validates restore-over-existing-file handling, restore of deleted files, and age-based cleanup of `.stversions`.

Important APIs and helpers: `TestTrashcanArchiveRestoreSwitcharoo`, `TestTrashcanRestoreDeletedFile`, `TestTrashcanCleanOut`, plus local `readFile`/`writeFile` wrappers over `fs.Filesystem`. The tests build `config.FolderConfiguration` values with basic folder and versioning filesystems, then instantiate `newTrashcan`.

Control flow: files are written to the folder filesystem, archived into the version filesystem, and restored through `Versioner.Restore`. The switcharoo test confirms an existing live file is archived before the requested version is moved back. The cleanout test creates old and fresh files under `.stversions`, runs `Clean`, then checks both file removal and empty directory pruning.

State and persistence: all state is filesystem-backed under temporary directories. Version times for trashcan files are represented by mtime because filenames are untagged.

Dependencies and integration: depends on `lib/config`, `lib/fs`, and the trashcan implementation in this package. Test signals cover mtime truncation, version inventory, restore collision safety, and cleanup directory retention. Risks are mostly time granularity and untagged-name collision behavior.
