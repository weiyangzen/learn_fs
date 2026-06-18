<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/suite_test.go -->
# sources/sync-backup/kopia/cli/suite_test.go

## Purpose
Provides CLI package test-suite bootstrap and format-version parameterization.

## Important APIs, Types, And Functions
Defines `TestMain`, `formatSpecificTestSuite`, and tests `TestFormatV1`, `TestFormatV2`, and `TestFormatV3`, each invoking `testutil.RunAllTestsWithParam` with the corresponding `--format-version` flag and `format.Version`.

## Control Flow
When package tests run, `TestMain` delegates to shared test main setup. The format tests run all parameterized tests under each repository format version.

## State And Persistence Behavior
Persistent state is test-only: temporary repositories created by downstream tests under different format versions.

## Dependencies And Integration Points
Integrates `internal/testutil`, repository format constants, and the package's format-specific test plumbing.

## Risks And Edge Cases
Adding a new repository format requires updating this suite. Parameterized tests must read the provided suite parameter correctly.

## Test Signals
Signals are broad: many CLI tests run against all supported repository formats, catching format-specific command regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/suite_test.go -->
