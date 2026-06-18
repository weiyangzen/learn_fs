# sources/sync-backup/restic/internal/fs/node_unix_notlinux.go

Purpose: Non-Linux Unix timestamp restore helper.

Important APIs: `utimesNano`.

Control flow and state: Skips symlinks, then calls `syscall.UtimesNano` for other node types using access and modification timestamps.

Dependencies and integration: Used by generic metadata restore on Unix platforms other than Linux.

Risks: Symlink timestamps are not restored on these targets due to Go/platform limitations. It follows normal syscall behavior for permission and filesystem support errors.

Test signals: `node_test.go` has platform-aware timestamp assertions that skip symlink timestamp checks on Darwin/BSD/OpenBSD/NetBSD/Solaris.
