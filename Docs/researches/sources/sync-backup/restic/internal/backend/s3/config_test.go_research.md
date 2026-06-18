<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/config_test.go -->
# sources/sync-backup/restic/internal/backend/s3/config_test.go

## Purpose
Tests S3 config parsing defaults and invalid formats.

## Important APIs, Types, And Functions
newTestConfig, configTests, TestParseConfig, and TestParseError are key.

## Control Flow
Table cases verify endpoint, bucket, prefix, UseHTTP, connections, restore defaults, and cleaned prefixes.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on backend/test and strings/time.

## Risks And Edge Cases
Environment application and credential selection are not covered here.

## Test Signals
Good coverage for user-facing S3 repository syntax.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/s3/config_test.go -->
