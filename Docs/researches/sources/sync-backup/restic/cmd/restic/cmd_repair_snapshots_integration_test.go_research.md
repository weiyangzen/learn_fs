# sources/sync-backup/restic/cmd/restic/cmd_repair_snapshots_integration_test.go

Purpose: integration tests for snapshot repair after data or tree loss.

Important APIs/types/functions: `testRunRepairSnapshot`; `createRandomFile`; `TestRepairSnapshotsWithLostData`; `TestRepairSnapshotsWithLostTree`; `TestRepairSnapshotsWithLostRootTree`; `TestRepairSnapshotsIntact`.

Control flow and state: tests generate deterministic random files, create backups, remove packs to simulate missing data/tree blobs, rebuild index, run repair snapshots with and without `--forget`, then verify snapshot counts and `check` outcomes. Intact test verifies no new snapshot is created when no changes are needed.

Dependencies and integration points: uses pack removal helpers, repair index helper, forget/check/list helpers, and deterministic file data generation.

Risks: direct pack deletion assumes local backend behavior. Tests focus on repository consistency, not detailed restored file contents after repair.

Test signals: strong validation that repair snapshots creates fixed snapshots, optionally deletes broken originals, and does not alter intact snapshots.
