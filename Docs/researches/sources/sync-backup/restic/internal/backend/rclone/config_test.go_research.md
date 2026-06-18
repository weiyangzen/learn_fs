<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/config_test.go -->
# sources/sync-backup/restic/internal/backend/rclone/config_test.go

## Purpose
Tests rclone config parsing defaults.

## Important APIs, Types, And Functions
configTests and TestParseConfig are the test surface.

## Control Flow
A rclone: remote is parsed and compared with default program/args/connections/timeout values.

## State And Persistence Behavior
No persistent state.

## Dependencies And Integration Points
Depends on backend/test.ParseConfigTester.

## Risks And Edge Cases
Invalid config inputs are not covered in this file.

## Test Signals
Basic regression coverage for user-facing rclone repository syntax.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rclone/config_test.go -->
