<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/config.go -->
# sources/sync-backup/restic/internal/backend/test/config.go

## Purpose
Provides a generic helper for config parser tests.

## Important APIs, Types, And Functions
ConfigTestData and ParseConfigTester are the API.

## Control Flow
ParseConfigTester iterates table cases, calls a parser, and reflect.DeepEqual compares the result against expected config.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on fmt, reflect, testing.

## Risks And Edge Cases
Comparable generic bound is stricter than DeepEqual requires but works for current config structs.

## Test Signals
Used by local, rclone, rest, s3, sftp, swift config tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/test/config.go -->
