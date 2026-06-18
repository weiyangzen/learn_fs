# sources/sync-backup/restic/cmd/restic/cmd_forget_integration_test.go

Purpose: integration tests for forget safety behavior.

Important helpers/tests: `testRunForgetMayFail` and `testRunForget` invoke `runForget` with a small prune max-unused option. `TestRunForgetSafetyNet` creates two snapshots for a host, verifies invalid keep-tag policy refuses to delete the last snapshot in a group, verifies bare `--unsafe-allow-remove-all` is rejected without filters, verifies forget without policy is rejected, and verifies filtered unsafe remove-all deletes matching snapshots.

State/persistence: creates a real test repository, runs backups, then deletes snapshot objects during the accepted unsafe-filter case.

Dependencies/integration: backup, snapshot listing, `data.SnapshotGroupByOptions`, `data.SnapshotFilter`, and prune option validation.

Risks/test signals: focused on safety rails rather than all retention policy combinations. It is important because forget is destructive.
