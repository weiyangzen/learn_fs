# sources/sync-backup/restic/cmd/restic/find_test.go

Purpose: unit tests for snapshot host filter finalization.

Important APIs/types/functions: `TestSnapshotFilter`.

Control flow and state: table-driven cases set `RESTIC_HOST`, parse flags through both single and multi snapshot filter initializers, call `finalizeSnapshotFilter`, and compare resulting `Hosts`.

Dependencies and integration points: uses pflag, `data.SnapshotFilter`, and restic test assertions.

Risks: only host finalization is tested; tag/path filtering and `FindFilteredSnapshots` channel behavior are not covered here.

Test signals: protects semantics that environment default applies only when the host flag is absent, and `--host ""` clears the default.
