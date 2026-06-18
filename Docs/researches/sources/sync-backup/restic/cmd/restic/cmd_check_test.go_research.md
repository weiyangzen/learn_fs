# sources/sync-backup/restic/cmd/restic/cmd_check_test.go

Purpose: unit tests for check option parsing, pack-subset selection, and temporary cache handling.

Important tests: `TestParsePercentage`, `TestStringToIntSlice`, `TestSelectPacksByBucket`, `TestSelectRandomPacksByPercentage`, `TestSelectNoRandomPacksByPercentage`, `TestSelectRandomPacksByFileSize`, and `TestSelectNoRandomPacksByFileSize` cover subset helper behavior. `TestPrepareCheckCache` and `TestPrepareDefaultCheckCache` validate creation and cleanup of temporary cache directories.

State/persistence: uses temporary directories and generated restic IDs. Cache tests create and remove `restic-check-cache-*` dirs and verify cleanup.

Dependencies/integration: uses `global.Options`, `progress.NewNoopPrinter`, `internal/restic`, and `rtest`.

Risks/test signals: random selection tests assert counts but not deterministic identity. Cache cleanup assertions protect against stale check caches and accidental use of persistent cache when `--with-cache` is absent.
