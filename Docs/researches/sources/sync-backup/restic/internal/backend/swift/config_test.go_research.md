<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/config_test.go -->
# sources/sync-backup/restic/internal/backend/swift/config_test.go

## Purpose
Tests Swift config parsing and invalid repository strings.

## Important APIs, Types, And Functions
configTests, TestParseConfig, configTestsInvalid, and TestParseConfigInvalid are important.

## Control Flow
Valid cases assert container, prefix, and default connections; invalid cases ensure malformed Swift URLs are rejected.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on backend/test.ParseConfigTester.

## Risks And Edge Cases
Environment auth mapping is not tested in this file.

## Test Signals
Good signal for Swift repository location syntax.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/swift/config_test.go -->
