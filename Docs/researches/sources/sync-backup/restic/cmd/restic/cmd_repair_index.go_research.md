# sources/sync-backup/restic/cmd/restic/cmd_repair_index.go

Purpose: implements `restic repair index` and deprecated `rebuild-index`, rebuilding repository indexes from pack files.

Important APIs/types/functions: `RepairIndexOptions`; `newRepairIndexCommand`; `newRebuildIndexCommand`; `runRebuildIndex`.

Control flow and state: command opens repository with an exclusive lock and calls `repository.RepairIndex`, passing `ReadAllPacks`. It prints `done` on success. The deprecated command creates a separate options capture to avoid sharing state with replacement command.

Dependencies and integration points: repository index repair logic lives in `internal/repository`; command exposes it with locking and progress.

Risks: index rebuild is repository-mutating and can fail in append-only backends when obsolete indexes cannot be removed. `--read-all-packs` is more expensive but can recover from worse index damage.

Test signals: integration tests verify duplicate-pack index repair, damaged index reads, and append-only removal failure.
