<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_expire.go -->
# sources/sync-backup/kopia/cli/command_snapshot_expire.go

## Purpose
Implements `snapshot expire`, which applies retention policy to selected sources or all sources and optionally deletes expired snapshots.

## Important APIs, Types, And Functions
Defines `commandSnapshotExpire`, `getSnapshotSourcesToExpire`, and `run`. It uses `snapshot.ListSources`, `snapshot.ParseSourceInfo`, and `policy.ApplyRetentionPolicy`.

## Control Flow
The command resolves target sources from `--all` or path args, sorts them for deterministic processing, applies retention for each source, and logs either dry-run counts or confirmed deletion counts.

## State And Persistence Behavior
Persistent state changes occur only when `--delete` is set; then retention application deletes snapshot manifests selected by policy. Without `--delete`, it is advisory.

## Dependencies And Integration Points
Integrates snapshot source listing, source-info parsing, repository writer actions, retention policy code, and logging.

## Risks And Edge Cases
No explicit validation prevents empty source list without `--all`; that results in a no-op. Retention policy behavior is delegated, so CLI tests need representative policies to detect regressions.

## Test Signals
Tests should cover all-source and explicit-source modes, dry-run messages, confirmed deletion, ordering, empty/no-delete cases, and parse failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_expire.go -->
