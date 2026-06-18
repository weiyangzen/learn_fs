# sources/sync-backup/restic/internal/fs/stat_unix.go

Purpose: Generic Unix stat conversion for non-Windows, non-Darwin, non-FreeBSD, non-NetBSD targets.

Important APIs: `extendedStat` and `ExtendedFileInfo.RecallOnDataAccess`.

Control flow and state: Extracts common stat fields from `syscall.Stat_t`, including nanosecond timestamps from `Atim`, `Mtim`, and `Ctim`. `RecallOnDataAccess` returns false.

Dependencies and integration: Provides metadata for Linux and other Unix-like backup/restore paths.

Risks: No cloud-placeholder detection here. Platform build tags must exclude syscall layouts that do not have these fields.

Test signals: Linux node/stat/no-atime tests exercise this implementation.
