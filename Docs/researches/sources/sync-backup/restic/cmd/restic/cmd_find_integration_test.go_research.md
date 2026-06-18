# sources/sync-backup/restic/cmd/restic/cmd_find_integration_test.go

Purpose: integration tests for `restic find` path, JSON, ordering, time validation, and pack/object lookup modes.

Important tests: `TestFind` checks normal path pattern results. `TestFindJSON` verifies JSON match grouping and tree ID searches. `TestFindSorting` checks default newest-first and `--reverse` oldest-first ordering. `TestFindInvalidTimeRange` validates oldest/newest guardrails. `TestFindPackfile` and `TestFindPackID` inspect repository indexes to locate pack IDs, then verify `--pack` JSON output maps pack contents back to snapshot paths and object types.

State/persistence: creates backups in temp repositories, loads indexes, and captures command output. It reads pack/blob metadata but does not mutate repositories after backup.

Dependencies/integration: backup helpers, repository read locks, JSON decoding, progress printers, and platform path normalization.

Risks/test signals: Windows path normalization requires trimming drive-specific prefixes. These tests are a strong contract for JSON consumers and troubleshooting workflows.
