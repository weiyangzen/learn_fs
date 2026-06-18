# sources/user-network-fs/gcsfuse/tools/integration_tests/release_version/setup_test.go

## Purpose

This harness prepares the release-version test package. The package does not mount GCSFuse; it only needs an available `gcsfuse` binary.

## Important APIs, Types, and Functions

`TestMain` parses setup flags, loads or synthesizes `ReleaseVersion` config, skips mounted-directory mode, calls `setup.SetUpTestDirForTestBucket`, runs tests, and exits with the result.

## Control Flow

After config loading, any non-empty `GKEMountedDirectory` causes an immediate skip with exit code 0. Otherwise, setup prepares the test directory and binary environment, then `m.Run` executes `TestReleaseVersion`.

## State and Persistence Behavior

The harness may create standard integration-test temp directories through setup but creates no bucket objects and performs no mount/unmount. It relies on setup to make the correct binary discoverable.

## Dependencies and Integration Points

It depends on `setup` and `test_suite` helpers. It is included in e2e package arrays for flat/HNS/zonal runs but is independent of bucket type except for setup plumbing.

## Risks and Edge Cases

Skipping mounted-directory mode means release-version coverage is absent in environments that only provide an already-mounted directory. If setup does not put the intended binary first in `PATH`, the test may inspect a system-installed version instead.

## Test Signals

Harness success is simply execution of the version-format test in a non-mounted-directory environment. Failures point to binary setup or CLI output issues.
