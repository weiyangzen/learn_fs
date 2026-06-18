# sources/sync-backup/restic/internal/fs/setflags_linux_test.go

Purpose: Linux test for `O_NOATIME` behavior.

Important APIs: `TestNoatime` and `supportsNoatime`.

Control flow and state: Creates an owned temp file, writes data, records access time, calls `setFlags`, reads one byte, then asserts atime did not change. The support helper only runs on known compatible filesystem magic values.

Dependencies and integration: Validates `setflags_linux.go` and `ExtendedStat` access-time extraction.

Risks: Skips on many filesystems; timestamp granularity and mount options could affect behavior.

Test signals: Confirms the optimization works where expected and avoids false failures elsewhere.
