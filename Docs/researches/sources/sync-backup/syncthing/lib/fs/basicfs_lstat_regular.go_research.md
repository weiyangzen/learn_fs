## sources/sync-backup/syncthing/lib/fs/basicfs_lstat_regular.go

Purpose: Default non-Linux/non-Android/non-Windows `Lstat` implementation.

Important APIs/types/functions: `BasicFilesystem.underlyingLstat`.

Control flow: Directly returns `os.Lstat(name)`.

State and persistence: Read-only metadata access.

Dependencies and integration points: Used by `BasicFilesystem.Lstat` on supported fallback platforms.

Risks: No platform-specific correction is applied.

Test signals: Build-tag compile and generic filesystem tests.
