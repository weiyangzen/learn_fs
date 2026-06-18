
# sources/sync-backup/restic/internal/repository/prune.go

Purpose: plans and executes repository pruning: deciding which packs to keep, repack, remove, or ignore, while preserving all used blobs and rewriting indexes.

Important APIs and types include `PruneOptions`, `PruneStats`, `PrunePlan`, `PlanPrune`, `packInfoFromIndex`, `calculateTargetPacksize`, `decidePackAction`, `PrunePlan.Execute`, and `deleteFiles`. `PlanPrune` obtains used blobs from a caller callback, derives per-pack usage and duplicate accounting from the index, selects actions, adjusts keep blobs for repacking, and calculates JSON-ready summary stats. `packInfoFromIndex` verifies every used blob exists, handles duplicate blob selection, and computes sizes. `decidePackAction` validates listed packs against index sizes, identifies unreferenced or missing packs, prioritizes repack candidates, and respects max unused/repack limits and compression repair needs.

Execution removes unreferenced packs first, repacks selected packs via `CopyBlobs`, rewrites or deletes indexes, removes old packs, optionally rebuilds fallback indexes for unsafe recovery, and clears the in-memory index. Risks include preventing data loss when indexes are incomplete, duplicate accounting, missing pack handling, dry-run differences, context cancellation, and pack size heuristics. Tests cover normal prune, small packs, duplicate MaxUnused accounting, and recovery-related paths.
