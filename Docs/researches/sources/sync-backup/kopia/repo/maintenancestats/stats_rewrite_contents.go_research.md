# sources/sync-backup/kopia/repo/maintenancestats/stats_rewrite_contents.go

Purpose: records content rewrite counts and byte totals.

Important APIs/types/functions: `RewriteContentsStats`, `WriteValueTo`, `Summary`, and `Kind`.

Control flow: writes to-rewrite, rewritten, and retained counters/sizes into content logs and formats a human summary.

State/persistence behavior: persisted in schedule extras after quick or full content rewrite tasks.

Dependencies/integration: produced by `RewriteContents` and registered in `BuildFromExtra`.

Risks/test signals: rewritten vs retained separation supports safety diagnostics. Builder and content rewrite tests validate JSON and selected stats values.
