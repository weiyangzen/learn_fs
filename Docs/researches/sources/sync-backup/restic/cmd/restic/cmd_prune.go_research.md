# sources/sync-backup/restic/cmd/restic/cmd_prune.go

Purpose: implements `restic prune`, planning and executing repository cleanup of unneeded data.

Important APIs/types/functions: `PruneOptions`; `AddFlags`; `AddLimitedFlags`; `verifyPruneOptions`; `runPrune`; `runPruneWithRepo`; `printPruneStats`; `getUsedBlobs`.

Control flow and state: option verification parses max unused space, max repack size, small-pack threshold, and unsafe no-space recovery. `runPrune` rejects incompatible compression/no-lock settings, opens an exclusive lock unless dry-run/no-lock is used, validates unsafe recovery by exact repository ID, and calls `runPruneWithRepo`. The latter loads the index, builds `repository.PruneOptions`, calls `repository.PlanPrune` with a callback that finds used blobs from snapshots, prints stats or JSON, triggers GC, then executes the plan. Persistent mutations can include repacking, deleting packs/indexes, and cleaning unreferenced data unless dry-run.

Dependencies and integration points: deeply depends on `internal/repository` prune planner/executor, `data.ForAllSnapshots`, `data.FindUsedBlobs`, UI byte parsing/formatting, and locks.

Risks: destructive behavior makes lock and option validation important. Unsafe recovery disables repacking and requires exact repo ID. Percent parsing forbids values >=100. JSON output bypasses text stats.

Test signals: prune integration tests cover max-unused variants, unsafe recovery mode, damaged and edge-case repos, small-pack threshold, and JSON stats.
