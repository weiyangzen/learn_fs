
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_fail_test.go

## Purpose
Validates snapshot failure handling around permission errors, fail-fast behavior, ignored file/dir errors, partial snapshot reporting, JSON output accounting, and environment/flag overrides.

## Important APIs, Types, And Functions
- `TestSnapshotNonexistent` checks missing source failure.
- `TestSnapshotFail_Default`, `TestSnapshotFail_DefaultJSONOutput`, `TestSnapshotFail_EnvOverride`, `TestSnapshotFail_NoFailFast`, and `TestSnapshotFail_FailFast` run the same permission matrix with different fail-fast and output modes.
- `expectedSnapshotResult`, `parsedSnapshotResult`, `testSnapshotFail`, `testSnapshotFailCases`, and `testPermissions` define expected success/error/partial outcomes.
- `createSimplestFileTree` creates deterministic nested dirs/files/empty dirs.
- `parseSnapshotResultFromLog` parses stderr using regexes for created snapshot, fatal error count, ignored error count, and partial status.
- `parseSnapshotResultJSON` extracts the same fields from `snapshot.Manifest` JSON.

## Control Flow
Tests skip on Windows and root, then create nested directory trees and iterate combinations of `--ignore-dir-errors`, `--ignore-file-errors`, permission modes, and snapshot source/modified entry relationships. Each subtest changes permissions, runs snapshot create, optionally restores successful snapshots, then validates parsed result counters.

## State And Persistence Behavior
Persists policies for ignore-file/dir behavior per source and snapshot manifests, including partial/incomplete metadata and root directory summary counters. The test carefully restores original permissions through cleanup to avoid undeletable temp trees.

## Dependencies And Integration Points
Uses `snapshot.Manifest`, `testenv`, `testdirtree`, `testutil`, OS permission bits, environment variable `KOPIA_SNAPSHOT_FAIL_FAST`, and CLI flags. Integrates filesystem permission errors, policy inheritance, CLI logging, JSON manifest summaries, and restore.

## Risks And Edge Cases
Platform and user identity are major constraints: the suite skips on Windows and root. Permission semantics differ across filesystems, and random `inherit` selection introduces minor non-determinism in case names/configuration. Regexes are coupled to CLI log text, while JSON parsing is coupled to manifest summary fields.

## Test Signals
High signal for error accounting and fail-fast behavior, especially consistency between text output and JSON output.
