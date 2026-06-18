<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/log_rotation/logrotate_logfile_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/log_rotation/logrotate_logfile_test.go

## Purpose

This file drives filesystem operations until gcsfuse rotates its log, then validates the expected active, backup, compressed/uncompressed, and stderr log file set and size limits.

## Important APIs, Types, and Functions

Helpers include `runOperationsOnFileTillLogRotation`, `runParallelOperationsInMountedDirectoryTillLogRotation`, and `validateLogFileSize`. The test uses `operations.GenerateRandomData`, `CreateFileWithContent`, `ReadFile`, `StatFile`, `ReadDirectory`, and `operations.RetryUntil`.

## Control Flow

Each worker creates a 5 MiB file and repeatedly reads it to generate trace logs. It watches `cfg.LogFile` size and exits when the active file size drops, indicating rotation. Five workers run in parallel; the outer test repeats this four times. It then reads the log directory with retry, counts the active `.log`, rotated `.log.gz` or uncompressed files, and stderr files, and validates total counts and size caps for active and uncompressed rotated logs.

## State and Persistence Behavior

State includes large test files under the mount, active log file growth, rotated backup files, and optional compressed backups. Rotation is inferred from active log size decreasing, not from a rotation API.

## Dependencies and Integration Points

It relies on constants and `cfg.LogFile` from `log_rotation_test.go`, setup mount directory state, and retry utilities. It exercises gcsfuse's internal lumberjack-style rotation behavior through real file operations.

## Risks and Test Signals

The loop can run long if logs are not generated or stat intermittently fails; one stat retry is allowed. Directory count includes stderr logs and assumes no unrelated files in the log directory. Passing signals are exactly expected log counts and size-bounded active/uncompressed logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/log_rotation/logrotate_logfile_test.go -->
