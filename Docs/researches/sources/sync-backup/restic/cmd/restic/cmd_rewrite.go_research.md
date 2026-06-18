# sources/sync-backup/restic/cmd/restic/cmd_rewrite.go

Purpose: implements `restic rewrite`, creating replacement snapshots with files excluded/included, metadata changed, or summary records added.

Important APIs/types/functions: `snapshotMetadataArgs.convert`; `RewriteOptions`; `rewriteSnapshot`; `filterAndReplaceSnapshot`; `runRewrite`; `gatherIncludeFilters`; `gatherExcludeFilters`.

Control flow and state: `runRewrite` requires some action, rejects simultaneous include/exclude, opens append lock for additive rewrites or exclusive lock when `--forget` may remove originals, memoizes snapshots, loads index, then rewrites each filtered snapshot. `rewriteSnapshot` builds include/exclude walkers and optional summary generation. `filterAndReplaceSnapshot` uploads the new tree, handles empty results, compares tree/metadata/summary to skip no-ops, saves a new snapshot with `Original` set, adds a tag unless forgetting, applies metadata, and optionally removes the old snapshot.

Dependencies and integration points: depends on filter package, walker snapshot-size rewriter, repository blob uploader, data snapshot save/remove, and shared snapshot filter helper. Repair snapshots reuses `filterAndReplaceSnapshot`.

Risks: rewrite can duplicate snapshots or delete originals. Include mode keeps explicitly matched empty directories; include-nothing with `--forget` preserves original snapshot. Time parsing uses `global.TimeFormat` in local time. No-op detection must include summary equality.

Test signals: rewrite integration tests cover exclude/additive, unchanged no-op, replace with forget, metadata changes, summary generation, include modes, exclude files, contradiction, empty directory include, and include-nothing preservation.
