# sources/sync-backup/restic/cmd/restic/cmd_check_integration_test.go

Purpose: integration helpers and tests for `runCheck`.

Important helpers/tests: `testRunCheck`, `testRunCheckMustFail`, `testRunCheckOutput`, and `testRunCheckOutputWithOpts` wrap `runCheck` in captured terminal environments. `TestCheckWithSnaphotFilter` creates two backups and verifies full and latest-only `--read-data` output counts, plus `--read-data-subset` filtered-output signaling.

State/persistence: creates repositories through backup helpers and reads them with check. It does not repair state.

Dependencies/integration: relies on backup fixtures, `global.Options`, captured stdout helpers, and `CheckOptions`.

Risks/test signals: output substring assertions can be brittle if progress formatting changes. The file provides an important integration signal that snapshot filtering affects both snapshot and pack counts.
