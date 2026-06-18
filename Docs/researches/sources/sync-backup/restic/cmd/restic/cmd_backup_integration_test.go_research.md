# sources/sync-backup/restic/cmd/restic/cmd_backup_integration_test.go

Purpose: integration coverage for `runBackup` against real test repositories and filesystem fixtures.

Important helpers/tests: `testRunBackupAssumeFailure` and `testRunBackup` invoke `runBackup` through terminal/test environment helpers. Tests cover normal backup/restore/check cycles, filesystem snapshots on Windows, relative-path parent selection, VSS snapshot isolation, dry-run non-persistence, missing source errors, self-healing after deleted packs, tree load repair behavior, exclude patterns, unreadable files, incremental repository growth, tags, program version, quiet mode, hardlinks, stdin-from-command variants, empty passwords, and `--skip-if-unchanged`.

Control flow/state: tests initialize repositories, create backup fixtures, run backup, list snapshots, run check, restore contents, remove packs for damage scenarios, and compare filesystem outputs. Several tests mutate repository internals to exercise repair/self-healing behavior.

Dependencies/integration: uses `withTestEnvironment`, restore/list/check helpers, `internal/data`, `internal/fs`, `internal/restic`, and tar fixtures.

Risks/test signals: platform-specific tests skip when prerequisites are absent, especially Windows VSS and hardlink fixture availability. These tests are the primary behavioral signal for backup's repository mutations and partial failure semantics.
