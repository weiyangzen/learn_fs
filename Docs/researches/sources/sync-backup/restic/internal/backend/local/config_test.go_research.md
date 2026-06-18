<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/config_test.go -->
# sources/sync-backup/restic/internal/backend/local/config_test.go

## Purpose
Table-tests local backend config parsing.

## Important APIs, Types, And Functions
configTests and TestParseConfig are the test surface.

## Control Flow
Each input is parsed and compared against expected Config with default Connections set to 2.

## State And Persistence Behavior
No persistence.

## Dependencies And Integration Points
Uses backend/test.ParseConfigTester.

## Risks And Edge Cases
The tests do not cover invalid prefixes or empty paths.

## Test Signals
Good signal that ParseConfig preserves platform path syntax.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/local/config_test.go -->
