<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/config_test.go -->
# sources/sync-backup/restic/internal/backend/sftp/config_test.go

## Purpose
Tests SFTP config parsing and invalid URL forms.

## Important APIs, Types, And Functions
configTests, TestParseConfig, configTestsInvalid, and TestParseConfigInvalid are key.

## Control Flow
Table cases verify user, host, port, cleaned path, connection defaults, IPv6, and user names containing @.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on backend/test.ParseConfigTester.

## Risks And Edge Cases
Does not cover tilde rejection explicitly in the visible table.

## Test Signals
Good coverage for user-facing SFTP location syntax.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/sftp/config_test.go -->
