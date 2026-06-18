<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_restore_test.go -->
# sources/sync-backup/kopia/cli/command_restore_test.go

Purpose: unit tests for restore snapshot-time parsing and latest/oldest filter construction.

Important APIs/types/functions: `TestRestoreSnapshotMaxTime`, `TestRestoreSnapshotFilter`, `computeMaxTime`, `createSnapshotTimeFilter`, and `clock.Now`.

Control flow: the max-time test computes expected boundary times for `yesterday`, day/month/year ago spellings, compound ago expressions, `last-month`, `last-year`, and partial absolute timestamps from year down to seconds. The filter test verifies `latest` selects index 0 and `oldest` selects the last candidate.

State/persistence behavior: no repository or filesystem mutation. Tests operate entirely on time values and filter closures.

Dependencies/integration: validates local time assumptions and supported input formats for path-based restore. Risks/test signals: tests depend on `clock.Now()` and local timezone, but compare derived values from the same clock snapshot to reduce flakiness.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_restore_test.go -->
