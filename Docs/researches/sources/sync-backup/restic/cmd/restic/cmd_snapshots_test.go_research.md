# sources/sync-backup/restic/cmd/restic/cmd_snapshots_test.go

Purpose: regression test for empty snapshots JSON output.

Important APIs/types/functions: `TestEmptySnapshotGroupJSON`.

Control flow and state: calls `printSnapshotGroupJSON` with a nil snapshot group map for both grouped and ungrouped modes and checks the trimmed output is `[]`.

Dependencies and integration points: uses `strings.Builder` and restic test assertions.

Risks: small but important JSON compatibility contract; nil slices/maps must encode as empty arrays due explicit construction in implementation.

Test signals: protects regression for issue where empty output could be `null`.
