
# sources/sync-backup/kopia/tests/end_to_end_test/suite_test.go

## Purpose
Defines a parameterized test suite that runs selected end-to-end tests against Kopia repository format versions 1, 2, and 3.

## Important APIs, Types, And Functions
- `formatSpecificTestSuite` holds `formatFlags` and `formatVersion`.
- `TestFormatV1`, `TestFormatV2`, and `TestFormatV3` call `testutil.RunAllTestsWithParam` with `--format-version=1`, `2`, and `3` respectively.

## Control Flow
The parameterized runner discovers methods on `formatSpecificTestSuite` such as `TestSnapshotGC`, `TestSnapshotMigrate`, and `TestSnapshotVerifyTest`, running them for each configured format.

## State And Persistence Behavior
No direct repository mutation in this file; it passes format flags into tests that create their own repositories.

## Dependencies And Integration Points
Uses `internal/testutil` and `repo/format`. It is an integration point between suite-level parameterization and individual method-based tests.

## Risks And Edge Cases
Adding a method to `formatSpecificTestSuite` implicitly multiplies it across all formats. Tests must tolerate older format semantics or explicitly gate behavior.

## Test Signals
Ensures format-version coverage for method-based end-to-end tests.
