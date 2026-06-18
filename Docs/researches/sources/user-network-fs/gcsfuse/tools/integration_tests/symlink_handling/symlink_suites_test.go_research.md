# sources/user-network-fs/gcsfuse/tools/integration_tests/symlink_handling/symlink_suites_test.go

## Purpose

Defines the reusable symlink suite infrastructure and the standard/legacy suite types. It handles per-test mounting, directory setup, synthetic GCS symlink object creation, backing-object validation, and config-driven suite dispatch.

## Important APIs, control flow, and dependencies

`BaseSymlinkSuite` stores flags, mount directory, test directory, representation mode, link name, and target path. `SetupTest` mounts gcsfuse for non-GKE runs and creates unique names. `TearDownTest` unmounts, saves logs, and cleans the GCS prefix. Helpers include `createSymlink`, `createTempFile`, `validateBackingGCSObjectForSymlink`, and `createGCSSymlinkObject`, the latter using `client.NewWriter`. `RunTests` selects config items by `Run` name and splits flag strings with `strings.Fields`.

## State, persistence, dependencies, and integration points

The backing-object validator reads object attrs and contents from GCS to enforce representation details: standard symlinks must contain the target and both metadata keys, while legacy symlinks must have size zero, the old metadata key, and no standard marker. Synthetic object creation waits for size updates on zonal buckets.

## Risks and test signals

Risks include per-test mount overhead, flag parsing that depends on whitespace rather than comma splitting, and cleanup interactions with GKE mounted directories. Signals are no-error mount/setup, exact metadata/content assertions, and successful suite selection for both `TestStandardSymlinksTestSuite` and `TestLegacySymlinksTestSuite`.
