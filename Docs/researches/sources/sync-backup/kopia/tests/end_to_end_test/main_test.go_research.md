# sources/sync-backup/kopia/tests/end_to_end_test/main_test.go

## Purpose
Provides package-wide setup and cleanup for end-to-end tests by creating reusable source directory trees.

## Important APIs, Types, and Functions
Globals `sharedTestDataDirBase`, `sharedTestDataDir1`, `sharedTestDataDir2`, and `sharedTestDataDir3`. `oneTimeSetup`, `oneTimeCleanup`, and `TestMain`.

## Control Flow
Setup chooses an interesting temp directory, optionally extends the path to trigger long-filename behavior, creates three directory trees with different depth/file-size profiles, and stores paths in globals. `TestMain` runs setup before the package and delegates cleanup to `testutil.MyTestMain`.

## State and Persistence Behavior
Creates real shared source data on disk and removes it after tests. Many tests read these globals concurrently.

## Dependencies and Integration Points
Uses `testutil` path helpers and `testdirtree` generators. All end-to-end tests in the package depend on this setup.

## Risks
Shared immutable fixtures reduce setup cost but require tests not to mutate shared directories. Long path behavior is conditional and may reveal Windows/path bugs only in some environments.

## Test Signals
Setup failure aborts the package. The three fixture shapes support small-tree, large-file, and many-file test coverage.
