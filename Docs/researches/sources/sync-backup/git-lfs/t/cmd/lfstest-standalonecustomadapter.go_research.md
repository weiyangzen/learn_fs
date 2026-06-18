# sources/sync-backup/git-lfs/t/cmd/lfstest-standalonecustomadapter.go

Purpose: standalone custom transfer adapter that copies uploads/downloads to a local backup directory instead of proxying HTTP storage.

Important APIs/types/functions: `backupDir`, `main`, `writeToStderr`, `sendResponse`, `sendTransferError`, `sendProgress`, `performCopy`, `performDownload`, `performUpload`, and custom adapter protocol structs.

Control flow: requires `TEST_STANDALONE_BACKUP_PATH`, logs arguments, reads line-oriented JSON events. Upload copies request path to `<backupDir>/<oid>` with progress events. Download copies from backup to a temp file and returns the temp path. Init and terminate are acknowledged/logged.

State/persistence behavior: persists object bytes as files in the configured backup directory and creates temp download files.

Dependencies/integration: tests standalone custom transfer mode and progress reporting using `tools.CopyWithCallback`.

Risks: backup path is global and must be isolated by tests. Terminate only breaks the switch, not the scanner loop. Existing backup files are overwritten by `os.Create`.

Test signals: JSON complete/progress events, backup file contents, and stderr logs.
