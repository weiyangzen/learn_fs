<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/log_rotation/log_rotation_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/log_rotation/log_rotation_test.go

## Purpose

This package setup file configures gcsfuse log rotation integration tests. It creates a log directory, rewrites GKE-style paths for GCE, builds default log rotation flag sets, and runs the package under static mounting.

## Important APIs, Types, and Functions

It defines constants for test directory, maximum file size, expected active/backup/stderr log counts, temp directory, retry timing, and shared globals `storageClient`, `ctx`, and `cfg`. `setupLogFilePath` sets the concrete log path. `TestMain` owns config, client, mount, and cleanup lifecycle.

## Control Flow

When no `LogRotation` config exists, default flags set `--log-file`, `--log-rotate-max-file-size-mb=2`, `--log-rotate-backup-file-count=2`, compression true/false, and trace severity. Mounted-directory mode is explicitly skipped. GCE setup creates the temp log directory, overrides `/gcsfuse-tmp`, builds compatible flags, points `cfg.LogFile` to the current test log path, runs static mounting tests, cleans the GCS test directory, and exits.

## State and Persistence Behavior

The setup persists active and rotated log files under `setup.TestDir()/gcsfuse-tmp`. It also creates/cleans a GCS prefix for file operations used to generate logs.

## Dependencies and Integration Points

It depends on test-suite config, Cloud Storage client creation, static mounting, path override helpers, and cleanup utilities. `logrotate_logfile_test.go` relies on `cfg.LogFile` and log count constants.

## Risks and Test Signals

The test is disabled for mounted-directory runs and assumes local access to log paths. Success is the package mounting with rotation flags and later tests observing expected rotated files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/log_rotation/log_rotation_test.go -->
