# sources/user-network-fs/gcsfuse/tools/integration_tests/symlink_handling/symlink_handling_test.go

## Purpose

Bootstraps the symlink-handling integration package and defines metadata constants for the standard and legacy GCS symlink representations. It runs both standard and legacy symlink suites against configured or fallback mounts.

## Important APIs, control flow, and dependencies

`TestMain` loads `cfg.SymlinkHandling`, creates fallback `ConfigItem`s for `TestStandardSymlinksTestSuite` with `--enable-standard-symlinks=true` and `TestLegacySymlinksTestSuite` with `--enable-standard-symlinks=false`, initializes the environment with `setup.TestEnvironment`, creates a storage client, and handles GKE mounted-directory versus static mount setup. Constants are `TestDirName`, `SymlinkMetadataKey` (`gcsfuse_symlink_target`), and `StandardSymlinkMetadataKey` (`goog-reserved-file-is-symlink`).

## State, persistence, dependencies, and integration points

The shared `testEnv` holds the storage client, context, and config pointer. Static mount mode calls `setup.SetUpTestDirForTestBucket` and `setup.OverrideFilePathsInFlagSet` so paths embedded in flags point at local test directories. Cleanup removes the symlink test directory from GCS after the package run.

## Risks and test signals

Risks include wrong metadata-key interpretation, config `Run` names not matching suite dispatch, and cleanup deleting the wrong prefix for only-dir mounts. Test signals come from the downstream suite tests plus successful initialization in both standard and legacy modes.
