## sources/sync-backup/syncthing/lib/fs/basicfs_lstat_broken.go

Purpose: Linux/Android `Lstat` workaround for transient `EINTR`.

Important APIs/types/functions: `BasicFilesystem.underlyingLstat`.

Control flow: Calls `os.Lstat` up to ten times, sleeping an increasing number of milliseconds after `PathError` with `EINTR`, and returns on success or non-EINTR error.

State and persistence: Read-only metadata access.

Dependencies and integration points: Used by `BasicFilesystem.Lstat` on Linux/Android.

Risks: Retry loop hides repeated EINTR for up to a small bounded delay; after ten retries it returns the last result.

Test signals: No direct tests in subset; motivated by Android-specific behavior.
