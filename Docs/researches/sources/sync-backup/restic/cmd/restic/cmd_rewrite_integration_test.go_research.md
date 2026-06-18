# sources/sync-backup/restic/cmd/restic/cmd_rewrite_integration_test.go

Purpose: integration coverage for snapshot rewrite features and edge cases.

Important APIs/types/functions: `testRunRewriteExclude`; `testRunRewriteWithOpts`; `testLsOutputContainsCount`; `createBasicRewriteRepo`; `createBasicRewriteRepoWithEmptyDirectory`; `getSnapshot`; tests for rewrite, no-op, replace, metadata, summary, include/exclude, contradictions, empty directory, and include nothing.

Control flow and state: tests create real snapshots, run rewrite with different options, inspect snapshot counts/IDs, load snapshots to compare summaries/metadata, use `ls` to verify retained paths, and run prune/check when old data becomes unused.

Dependencies and integration points: uses filter option structs, list/check/prune helpers, snapshot loading, and ls helpers.

Risks: several assertions depend on fixture file names and sizes. Helper `testRunRewriteWithOpts` currently asserts success before returning nil, so callers cannot inspect expected errors through it.

Test signals: validates rewrite correctness for additive and replacement modes, summary recalculation, metadata conversion, and include/exclude tree semantics.
