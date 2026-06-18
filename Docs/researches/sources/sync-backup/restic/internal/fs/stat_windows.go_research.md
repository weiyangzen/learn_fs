# sources/sync-backup/restic/internal/fs/stat_windows.go

Purpose: Windows stat conversion and cloud-placeholder detection.

Important APIs: `extendedStat` and `ExtendedFileInfo.RecallOnDataAccess`.

Control flow and state: Converts `Win32FileAttributeData` into size and timestamps, using LastWriteTime as ChangeTime because Windows lacks Unix ctime semantics. `RecallOnDataAccess` checks `FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS`.

Dependencies and integration: Feeds Windows node conversion and backup skip/download decisions.

Risks: Panics if `os.FileInfo.Sys()` is not `*syscall.Win32FileAttributeData`. ChangeTime semantics differ from Unix.

Test signals: `stat_windows_test.go` covers real regular files and mocked recall-on-access attributes.
