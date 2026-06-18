# sources/sync-backup/restic/internal/fs/node_linux.go

Purpose: Linux timestamp restore that does not follow symlinks.

Important APIs: `utimesNano`.

Control flow and state: Converts nanosecond access/modification timestamps into `unix.Timespec` values and calls `unix.UtimesNanoAt` with `AT_SYMLINK_NOFOLLOW`.

Dependencies and integration: Used by `nodeRestoreTimestamps` for all node types on Linux.

Risks: Errors include missing paths and permission failures. Unlike some Unix targets, symlinks are handled rather than skipped.

Test signals: `node_linux_test.go` checks missing symlink timestamp restore returns a not-exist error including the path.
