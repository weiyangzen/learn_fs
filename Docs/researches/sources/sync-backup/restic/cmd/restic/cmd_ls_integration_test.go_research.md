# sources/sync-backup/restic/cmd/restic/cmd_ls_integration_test.go

Purpose: integration tests for `runLs` output modes over real test repositories.

Important APIs/types/functions: `testRunLsWithOpts`; `testRunLs`; `assertIsValidJSON`; `TestRunLsNcdu`; `TestRunLsSort`; `TestRunLsJson`.

Control flow and state: tests create backups from fixture data, then capture stdout from `runLs`. Ncdu cases verify valid top-level JSON for full and filtered listings. Sort tests compare exact text line order for size, extension, and default name order. JSON tests unmarshal the snapshot line and node lines and compare IDs and paths.

Dependencies and integration points: depends on backup/list helpers, `LsOptions`, `global.Options.JSON`, and restic fixture layout.

Risks: exact order/path assertions are fixture-coupled. JSON test uses a partial copy of output structs, which intentionally tracks public fields but can drift.

Test signals: confirms user-facing `ls` formats remain parseable and stable for common modes.
