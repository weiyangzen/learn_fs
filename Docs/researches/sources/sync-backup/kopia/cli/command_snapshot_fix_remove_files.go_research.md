<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix_remove_files.go -->
# sources/sync-backup/kopia/cli/command_snapshot_fix_remove_files.go

## Purpose
Implements `snapshot fix remove-files`, which rewrites snapshot trees to remove entries by object ID or filename pattern.

## Important APIs, Types, And Functions
Defines `commandSnapshotFixRemoveFiles`, `setup`, `rewriteEntry`, and `run`. Matching uses `slices.Contains` for object ID strings and `path.Match` for filename wildcard patterns.

## Control Flow
`run` requires at least one object ID or filename flag, then delegates to common snapshot rewrite. `rewriteEntry` returns nil for matched entries, causing the rewriter to omit them; unmatched entries are returned unchanged.

## State And Persistence Behavior
Committed runs persist updated snapshot manifests and rewritten directory trees. Dry-run rewrite work is reported but manifests are not updated.

## Dependencies And Integration Points
Integrates shared `commonRewriteSnapshots`, snapshot directory entry rewriting, repository writers, and Go path wildcard matching.

## Risks And Edge Cases
Filename matching is against `ent.Name`, not full path, so directory context is not matched by `--filename`. Invalid wildcard syntax aborts processing. Removing by object ID can affect multiple paths and snapshots.

## Test Signals
Tests should cover object-ID match, wildcard match, invalid wildcard, no criteria error, and commit versus no-commit behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix_remove_files.go -->
