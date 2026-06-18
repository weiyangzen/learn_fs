<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix.go -->
# sources/sync-backup/kopia/cli/command_snapshot_fix.go

## Purpose
Provides the `snapshot fix` parent and shared snapshot-rewrite machinery used by invalid-file repair and file-removal subcommands.

## Important APIs, Types, And Functions
Key symbols are `commandSnapshotFix`, `commonRewriteSnapshots`, invalid-entry constants, `failedEntryCallback`, `rewriteMatchingSnapshots`, `snapshotSizeDelta`, and `listManifestIDs`.

## Control Flow
Child commands configure a `snapshotfs.DirRewriter` with a callback, then `rewriteMatchingSnapshots` resolves target manifests from explicit IDs, sources, or all snapshots; groups them by source; computes metadata compression policy; rewrites each manifest; optionally saves updates when `--commit` is set; and logs old/new root IDs and size deltas.

## State And Persistence Behavior
Without `--commit`, rewritten manifests are not persisted. With commit, snapshot manifests are updated and new rewritten directory objects may be written. Directory read failures can fail, stub, or keep based on flags.

## Dependencies And Integration Points
Integrates snapshot manifest listing/loading/updating, policy metadata compression, `snapshotfs.NewDirRewriter`, repository writers, and unit formatting.

## Risks And Edge Cases
Dry-run still performs rewrite work and may create intermediate objects depending on rewriter behavior. Invalid directory handling supports only fail/stub/keep in shared setup, while invalid file handling adds remove in the child. Rewriting all snapshots can be expensive.

## Test Signals
Tests should cover manifest selection, commit versus dry-run, unchanged snapshots, compression policy propagation, size delta logging, and each invalid-directory handling mode.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix.go -->
