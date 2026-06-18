<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix_invalid_files.go -->
# sources/sync-backup/kopia/cli/command_snapshot_fix_invalid_files.go

## Purpose
Implements `snapshot fix invalid-files`, which verifies file object readability and rewrites snapshots to handle invalid file references.

## Important APIs, Types, And Functions
Defines `commandSnapshotFixInvalidFiles`, `setup`, `rewriteEntry`, and `run`. It creates a `snapshotfs.Verifier`, optionally preloads a blob map for direct repositories, and chooses a failed-file callback from fail/stub/keep/remove.

## Control Flow
`run` configures verifier options, builds the verifier, and delegates to shared rewrite machinery. For each non-directory entry, `rewriteEntry` calls `Verifier.VerifyFile`; failures are logged and transformed using the configured failed-file callback.

## State And Persistence Behavior
With commit, rewritten manifests persist changes such as stubs or removed entries. The verifier may use repository blob-map state to detect missing content efficiently.

## Dependencies And Integration Points
Integrates `snapshotfs.Verifier`, `blob.ReadBlobMap`, shared `commonRewriteSnapshots`, and repository direct/writer interfaces.

## Risks And Edge Cases
Verification percentage can leave some file contents unchecked. Blob-map availability differs for direct versus indirect repositories. Choosing keep can leave known-bad entries in manifests; remove/stub changes tree semantics.

## Test Signals
Test signals are corrupt content or deleted blob scenarios, each invalid-file handling mode, verify-percent behavior, direct-repo blob map use, and commit/no-commit differences.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_fix_invalid_files.go -->
