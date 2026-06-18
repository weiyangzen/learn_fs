# sources/sync-backup/kopia/repo/maintenance/maintenance_run.go

Purpose: orchestrates quick, full, and automatic maintenance under ownership, schedule, safety, and locking rules.

Important APIs/types/functions: `Mode`, `TaskType`, `shouldRun`, `RunExclusive`, `Run`, `runQuickMaintenance`, `runFullMaintenance`, task wrappers, `shouldQuickRewriteContents`, `shouldFullRewriteContents`, `shouldDeleteOrphanedPacks`, `hadRecentFullRewrite`, and `findSafeDropTime`.

Control flow: `RunExclusive` loads params, checks owner unless forced, resolves auto mode, takes a local flock on the config lock file, updates the schedule before work, validates clock skew from the schedule blob timestamp, refreshes indexes, and invokes the callback. `Run` dispatches quick or full mode. Quick mode prioritizes epoch maintenance when enabled, otherwise manages content rewrite, orphaned pack deletion, index compaction, and log cleanup. Full mode rewrites content, safely drops deleted content, deletes orphaned packs, optionally extends object locks, runs epoch cleanup, and cleans logs.

State/persistence behavior: mutates repository content/index/log/blob retention state and persists task history in the encrypted maintenance schedule. Schedule update before task execution prevents tight crash loops.

Dependencies/integration: ties together repository writer, content manager, epoch manager, content logs, flock locking, maintenance params, schedules, stats, snapshot GC safety, and pack/content rewrite helpers.

Risks/test signals: incorrect safety timing can delete data too early; local-only locking does not coordinate across hosts; clock skew checks refuse unsafe runs. Tests cover rewrite/delete decision functions, safe-drop timing, epoch quick maintenance, and schedule behavior.
