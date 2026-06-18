# sources/sync-backup/restic/internal/fs/setflags_linux.go

Purpose: Linux read optimization that attempts to prevent atime updates.

Important APIs: `setFlags`.

Control flow and state: Reads current file status flags with `F_GETFL`, then sets `O_NOATIME` in addition to existing flags with `F_SETFL`.

Dependencies and integration: Called after local files are opened for reading in `newLocalFile`; errors are intentionally ignored by production code but returned for tests.

Risks: `O_NOATIME` can fail unless the process owns the file or is privileged, and support depends on filesystem. Ignoring errors is expected.

Test signals: `setflags_linux_test.go` verifies atime is unchanged on filesystems known to support no-atime.
