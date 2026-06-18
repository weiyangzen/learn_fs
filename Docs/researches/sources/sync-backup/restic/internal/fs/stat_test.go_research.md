# sources/sync-backup/restic/internal/fs/stat_test.go

Purpose: Cross-platform tests for public `ExtendedStat`.

Important APIs: `TestExtendedStat` and `TestNilExtendPanic`.

Control flow and state: Writes a temp file, calls package `Lstat`, converts it, and compares modification time. The nil test recovers and asserts the panic message.

Dependencies and integration: Covers `stat.go` and platform `extendedStat` indirectly.

Risks: Minimal metadata assertion; detailed stat field checks live in node tests.

Test signals: Confirms basic wrapper behavior and deliberate nil panic.
