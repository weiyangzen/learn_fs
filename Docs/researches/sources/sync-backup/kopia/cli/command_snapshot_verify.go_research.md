<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_verify.go -->
# sources/sync-backup/kopia/cli/command_snapshot_verify.go

## Purpose
Implements `snapshot verify`, which walks snapshot trees, directory object IDs, file object IDs, or selected sources and verifies referenced repository content.

## Important APIs, Types, And Functions
Important functions are `setup`, `run`, `makeVerifyWalkerFunc`, `addExpectedWorkFromDirSummaryToVerifier`, `loadSourceManifests`, `noVerifyTargetArgsProvided`, and `loadSnapIDManifests`. It configures `snapshotfs.VerifierOptions` and uses `Verifier.InParallel`.

## Control Flow
`run` optionally disables index refresh for direct writers, builds verifier options including queue length, parallelism, max errors, JSON stats, and blob map, then runs parallel tree walking. The walker loads target manifests, creates snapshotfs roots, seeds expected totals from directory summaries, processes roots and explicit directory/file object IDs, and returns aggregate verifier errors.

## State And Persistence Behavior
The command is read-only, but it mutates in-memory verifier counters and may disable direct repository index refresh for performance. It observes blob maps, manifests, object graphs, and file content depending on verify percentage.

## Dependencies And Integration Points
Integrates snapshot manifest APIs, snapshotfs verifier/tree walker, direct repository blob map support, JSON output, runtime CPU defaults, and shared timestamp formatting.

## Risks And Edge Cases
Deprecated `--all-sources` has no effect. If no target args are provided, all manifests are verified, which can be expensive. `tw.Process` errors are intentionally ignored locally and aggregated by the verifier. Loading explicit snapshot IDs requires all requested IDs to exist.

## Test Signals
Tests should cover all target modes, JSON result output, max error threshold, verify file percent, missing manifests, blob-map acceleration, and explicit object ID parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_verify.go -->
