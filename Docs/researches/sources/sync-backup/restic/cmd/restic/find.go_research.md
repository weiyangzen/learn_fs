# sources/sync-backup/restic/cmd/restic/find.go

Purpose: centralizes snapshot filter flag registration, RESTIC_HOST defaulting, and filtered snapshot iteration.

Important APIs/types/functions: `initMultiSnapshotFilter`; `initSingleSnapshotFilter`; `finalizeSnapshotFilter`; `FindFilteredSnapshots`.

Control flow and state: flag helpers register host/tag/path filters for multi-snapshot and single-snapshot commands. `finalizeSnapshotFilter` applies `RESTIC_HOST` only when host flags were not set and treats an explicit single empty host as no host filter. `FindFilteredSnapshots` starts a goroutine, memoizes snapshot listing, delegates to `SnapshotFilter.FindAll`, logs per-snapshot errors, and sends successful snapshots on a channel while honoring context cancellation.

Dependencies and integration points: used by ls, restore, snapshots, stats, tag, rewrite, repair snapshots, and mount. Depends on pflag, `data.SnapshotFilter`, restic lister/loader interfaces, and progress printer.

Risks: goroutine logs errors rather than returning them to callers, so commands must check `ctx.Err` but cannot see all load failures as errors. Host defaulting semantics are subtle and user-facing.

Test signals: `find_test.go` covers RESTIC_HOST and explicit host flag combinations.
