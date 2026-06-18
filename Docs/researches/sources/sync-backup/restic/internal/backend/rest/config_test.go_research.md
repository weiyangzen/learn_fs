<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/config_test.go -->
# sources/sync-backup/restic/internal/backend/rest/config_test.go

## Purpose
Tests REST config parsing and password masking.

## Important APIs, Types, And Functions
parseURL, configTests, TestParseConfig, passwordTests, and TestStripPassword are key.

## Control Flow
Inputs are parsed with default connections and compared; masking tests call the factory StripPassword path to ensure registry integration.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Depends on net/url, backend/test, and rest factory functions.

## Risks And Edge Cases
Environment application is not covered in this file.

## Test Signals
Good regression signal for user-facing REST URLs and secret redaction.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/rest/config_test.go -->
