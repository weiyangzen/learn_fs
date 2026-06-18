<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/backend_test.go -->
# sources/sync-backup/restic/internal/backend/rclone/backend_test.go

## Purpose
Runs backend suite tests against rclone when the rclone binary is available.

## Important APIs, Types, And Functions
TestBackendRclone and BenchmarkBackendRclone are the main entry points.

## Control Flow
The test locates rclone, builds a temporary local remote, and runs the shared backend suite/benchmarks.

## State And Persistence Behavior
Uses subprocesses and temporary filesystem state behind rclone.

## Dependencies And Integration Points
Depends on rclone.NewFactory, backend/test Suite, os/exec, and internal/test helpers.

## Risks And Edge Cases
Skipped when rclone is missing; failures can come from external rclone behavior rather than restic code only.

## Test Signals
Provides integration coverage for the stdio REST bridge.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/backend_test.go -->
