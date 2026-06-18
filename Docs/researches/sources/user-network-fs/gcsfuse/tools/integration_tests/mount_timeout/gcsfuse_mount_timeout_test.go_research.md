<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/gcsfuse_mount_timeout_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/gcsfuse_mount_timeout_test.go

## Purpose

This file implements mount latency tests across bucket locations and client protocols. It measures repeated gcsfuse mount/unmount cycles and asserts the best observed mount time is below environment-specific thresholds.

## Important APIs, Types, and Functions

Types include `RegionWiseTimeouts`, `ZBMountTimeoutTestCaseConfig`, `MountTimeoutTest`, `NonZBMountTimeoutTest`, and `ZBMountTimeoutTest`. Core helpers are `SetupTest`, `TearDownTest`, `mountOrTimeout`, and `unmountAndWait`. Tests cover multi-region, dual-region, single-region, same-zone zonal, and cross-zone zonal buckets.

## Control Flow

`TestMountTimeout` chooses zonal or non-zonal suites based on `setup.IsZonalBucketRun()` and the `TEST_ENV` value set by package setup. Non-zonal GCE us-central uses strict region thresholds; other GCE regions use relaxed thresholds; non-GCE skips. `mountOrTimeout` constructs gcsfuse args with client protocol, trace logging, and log file, mounts/unmounts ten times, tracks the minimum duration, saves the log artifact on error, and fails if the minimum exceeds expected. `unmountAndWait` calls util unmount and polls `/proc/mounts` for up to five seconds.

## State and Persistence Behavior

Each test creates a temporary mount directory and log file path. It repeatedly mounts real buckets and immediately unmounts, leaving no intended bucket data. Timing state is in-memory, while logs persist as artifacts on failure.

## Dependencies and Integration Points

It depends on the built or installed gcsfuse binary, fusermount on Linux, bucket accessibility checks, cfg protocol constants, and package globals from `mount_timeout_test.go`.

## Risks and Test Signals

Latency tests are inherently environment-sensitive; they mitigate variance by using the minimum of ten attempts. Bucket accessibility, network, and `/proc/mounts` polling can affect results. Passing signal is all accessible buckets mounting under thresholds for selected protocols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/gcsfuse_mount_timeout_test.go -->
