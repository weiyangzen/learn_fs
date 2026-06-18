# sources/sync-backup/restic/cmd/restic/cmd_snapshots_integration_test.go

Purpose: integration coverage for snapshots JSON output, grouping, and latest filtering.

Important APIs/types/functions: `testRunSnapshots`; `TestSnapshotsGroupByAndLatest`.

Control flow and state: helper captures JSON snapshots and builds a map by ID plus newest pointer. The test creates two snapshots on the same host with different paths and increasing timestamps, runs `runSnapshots` in JSON mode with `GroupBy.Host` and `Latest: 1`, then asserts a single host group with no path/tag key and the second snapshot as the only entry.

Dependencies and integration points: uses backup helpers, snapshot map helpers, JSON structs from command code, and fixture data.

Risks: timestamp ordering depends on explicit one-second offset. JSON shape is part of the asserted contract.

Test signals: verifies grouping by host does not implicitly group by path and latest selection is per group.
