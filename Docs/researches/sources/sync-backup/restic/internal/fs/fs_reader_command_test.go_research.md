# sources/sync-backup/restic/internal/fs/fs_reader_command_test.go

Purpose: External-package tests for subprocess-backed readers.

Important APIs: `TestCommandReaderSuccess`, `TestCommandReaderFail`, `TestCommandReaderInvalid`, `TestCommandReaderEmptyArgs`, `TestCommandReaderOutput`, and `TestCommandReaderQuickClose`.

Control flow and state: Tests use simple shell commands (`true`, `false`, `echo`, `sleep`) to verify read, error, and close behavior. Quick close uses a timeout context and expects cancellation.

Dependencies and integration: Tests public `fs.NewCommandReader` behavior from package `fs_test`.

Risks: Assumes Unix-like commands exist in the test environment; less portable to minimal Windows shells.

Test signals: Confirms command exit failures propagate through reads and that closing kills a long-running command without waiting for the full sleep duration.
