<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_estimate_test.go -->
# sources/sync-backup/kopia/cli/command_snapshot_estimate_test.go

## Purpose
Tests user-visible behavior of `snapshot estimate` against a temporary filesystem repository and local directory tree.

## Important APIs, Types, And Functions
The file defines `TestSnapshotEstimate` and `TestSnapshotEstimate_NotADirectory`, using `testenv.NewCLITest`, in-process runner, `testutil.TempDirectory`, and stdout substring assertions.

## Control Flow
The main test creates three files, runs estimate, then adds ignore policies for filename and directory patterns and reruns estimate after each policy change. The second test creates a file and asserts estimation fails when the source is not a directory.

## State And Persistence Behavior
Test state includes a temporary filesystem repository, local temp files, and repository policy records created by `policy set --add-ignore`.

## Dependencies And Integration Points
Integrates the CLI command stack, repository creation, policy CLI, upload estimator, and output formatting.

## Risks And Edge Cases
Assertions depend on exact human-readable sizes and strings such as `Snapshot excludes no directories.`; formatting changes can break tests even when behavior is correct.

## Test Signals
The test is a strong signal for policy-aware estimate output. It does not cover JSON, quiet mode, upload-speed edge cases, or estimator error counts.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_snapshot_estimate_test.go -->
