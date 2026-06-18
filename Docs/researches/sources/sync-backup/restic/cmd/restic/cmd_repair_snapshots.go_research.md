# sources/sync-backup/restic/cmd/restic/cmd_repair_snapshots.go

Purpose: implements `restic repair snapshots`, rewriting broken snapshots with unreadable trees, invalid nodes, or missing file blobs removed/fixed.

Important APIs/types/functions: `RepairOptions`; `runRepairSnapshots`; walker `TreeRewriter`; shared `filterAndReplaceSnapshot` from rewrite command.

Control flow and state: opens an exclusive lock, using dry-run as no-lock allowance, memoizes snapshots, loads index, builds a tree rewriter. File nodes with invalid types are removed; missing content blobs are dropped and file size recalculated; unreadable subtrees become empty directories, while unreadable root trees cause snapshot removal. For each filtered snapshot it calls `filterAndReplaceSnapshot` with tag `repaired`, optional `--forget`, and no metadata changes. It reports modified count.

Dependencies and integration points: depends on snapshot filtering, repository blob lookup, `walker.NewTreeRewriter`, and rewrite's snapshot replacement helper.

Risks: command intentionally causes data loss to make snapshots consistent. It requires a correct index first. In-place node mutation during rewrite must not leak unexpected state. Root tree failures can delete snapshots.

Test signals: integration tests cover lost data blobs, lost subtrees, lost root trees, and intact snapshots remaining unchanged.
