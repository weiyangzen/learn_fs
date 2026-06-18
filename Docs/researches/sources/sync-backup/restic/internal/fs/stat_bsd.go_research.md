# sources/sync-backup/restic/internal/fs/stat_bsd.go

Purpose: FreeBSD/NetBSD `extendedStat` implementation.

Important APIs: `extendedStat` and `ExtendedFileInfo.RecallOnDataAccess`.

Control flow and state: Extracts stat fields from `syscall.Stat_t`, using BSD `Atimespec`, `Mtimespec`, and `Ctimespec`. `RecallOnDataAccess` always returns false.

Dependencies and integration: Feeds node metadata conversion on BSD targets.

Risks: No cloud-placeholder detection on BSD. Field type conversions must match platform syscall layout.

Test signals: Generic stat/node tests cover this on BSD builders.
