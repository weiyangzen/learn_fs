<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/core_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/core_test.go

## Purpose

This ogletest suite validates `Core` classification and sanity checks.

## Important APIs, Types, and Functions

`CoreTest` sets up a fake syncer bucket and simulated clock. Tests create GCS objects or folders, construct `inode.Core` values with different combinations of `FullName`, `MinObject`, `Folder`, and `Local`, then assert `Exists`, `Type`, and `SanityCheck`.

## Control Flow

Tests use `storageutil.CreateObject` and `bucket.CreateFolder` to obtain realistic metadata. They construct names with `NewRootName`, `NewFileName`, and `NewDirName`. Sanity tests mutate the relationship between name and object metadata to verify expected errors.

## State and Persistence Behavior

State is test-local fake bucket data and simulated clock. No persistent files are created.

## Dependencies and Integration Points

The suite covers `metadata.Type` mapping, fake storage, `gcsx.SyncerBucket`, storage utilities, HNS folder creation, and symlink-aware type classification indirectly through the default regular file path.

## Risks and Edge Cases

The tests protect nil-core behavior and objectless local file behavior, both of which are easy to regress. They do not construct an actual symlink metadata object in this file, so symlink type coverage depends on other suites.

## Test Signals

Signals include `RegularFileType`, `ExplicitDirType`, `ImplicitDirType`, `UnknownType`, nil/non-nil sanity-check results, and HNS folder explicit directory classification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/core_test.go -->
