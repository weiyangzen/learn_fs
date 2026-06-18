<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/mount_timeout_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/mount_timeout_test.go

## Purpose

This package setup file initializes mount-timeout and mount-access tests. It builds or locates gcsfuse, detects the execution environment, creates a storage client, and skips unsupported mounted-directory/GKE scenarios.

## Important APIs, Types, and Functions

Globals include `gBuildDir`, `gFusermountPath`, `gStorageClient`, `gCtx`, and `testBucket`. Constants define environment labels, bucket names, expected timeout thresholds, zonal bucket names, relaxed timeout, and log prefix. `findTestExecutionEnvironment` uses OpenTelemetry GCP resource detection. `TestMain` owns binary/client lifecycle.

## Control Flow

`findTestExecutionEnvironment` detects cloudtop/non-GCE via hostname, non-zonal GCE region via `cloud.region`, and zonal GCE via `cloud.availability_zone`, returning labels consumed by `TestMountTimeout`. `TestMain` parses flags, finds `fusermount` on Linux, reads config, skips mounted-directory runs, creates storage client, sets `TEST_ENV`, and either uses installed gcsfuse by setting `gBuildDir="/"` or builds gcsfuse into a temp directory via `util.BuildGcsfuse`. It runs tests, removes the build dir, and exits.

## State and Persistence Behavior

The file persists a temporary build directory and process environment variable `TEST_ENV` for the package. It owns the shared storage client and test bucket name.

## Dependencies and Integration Points

It depends on setup/test-suite config, `exec.LookPath`, OpenTelemetry GCP resource detector, Cloud Storage client helpers, and gcsfuse build utilities. Other mount_timeout files rely on its globals.

## Risks and Test Signals

Environment detection controls whether latency tests run or skip; detector failures can skip or relax coverage. Installed-package mode assumes binary layout rooted at `/`. Success is successful setup, binary availability, and correct environment label for downstream tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/mount_timeout_test.go -->
