# sources/sync-backup/kopia/repo/buildinfo_test.go

Purpose: unit tests for formatting VCS build settings into Kopia's build revision string.

Important APIs/types/functions: `TestGetRevisionString` supplies slices of `debug.BuildSetting` to `getRevisionString`.

Control flow: table cases cover no settings, dirty-only, time-only, time plus dirty, full revision, short revisions, and dirty full revision. Each subtest compares exact formatted output.

State and persistence behavior: no persistent state; the test avoids touching package globals by calling the helper directly.

Dependencies/integration: depends on standard `runtime/debug` settings shape and testify `require`.

Risks and edge cases: exact string assertions intentionally lock the current formatting contract, including leading hyphen when time is absent.

Test signals: failures indicate version output changed and downstream CLI or diagnostics expectations may need updates.
