# sources/sync-backup/kopia/cli/command_logs_cleanup.go

## Purpose
Log cleanup command that applies retention limits for encrypted repository log sessions, supporting age/count/total-size limits and dry-run mode.

## APIs, Types, and Functions
Important APIs include types `commandLogsCleanup`; functions/methods `setup`, `run`; Kingpin command(s) cleanup: Clean up logs; flags max-age: Maximal age, max-count: Maximal number of files to keep, max-total-size-mb: Maximal total size in MiB, dry-run: Do not delete.

## Control Flow, State, and Persistence
Control flow registers command(s) cleanup: Clean up logs, binds flags max-age: Maximal age, max-count: Maximal number of files to keep, max-total-size-mb: Maximal total size in MiB, dry-run: Do not delete, then runs through a direct repository write action. The implementation deletes blob storage objects. State and persistence: touches maintenance params, schedule, and maintenance statistics, encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, time, github.com/pkg/errors, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/maintenance. It integrates with Kopia repository internals such as kopia/repo, kopia/repo/maintenance plus external packages context, time, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: destructive modes require explicit confirmation/commit and should keep dry-run behavior tested. time/progress estimates are useful signals but can be flaky if asserted too tightly. no same-name test file is present in this subset; rely on integration tests or command-level coverage elsewhere.
