## sources/test-tools/syzkaller/syz-cluster/pkg/stats/worker.go

This file defines a periodic `stats.Worker` that recomputes denormalized per-series statistics. `NewWorker` accepts repositories and an interval, `Loop` ticks until context cancellation, `RunOnce` fetches outdated series in batches of ten, and `processSeries` calculates and stores stats.

The central state transition is `processSeries`: count prevented bugs for the current series, upsert a `db.SeriesStats` row with `StatsVersion: "v1"`, `PreventedBugs`, and `UpdatedAt`, then find previous versions of the same series and bulk-update their prevented bug counts to zero. This encodes the rule that only the latest version contributes prevented-bug totals.

Dependencies are `SeriesRepository`, `SeriesStatsRepository`, `StatsRepository`, context cancellation, and syzkaller logging. Integration points include dashboard/stat API queries and session-test-step data that feeds `CountPreventedBugs`. Risks include fixed batch size delaying catch-up on large backlogs, errors being logged but not retried immediately in the same tick, and stats-version changes requiring repository `ListOutdated` semantics to be correct.
