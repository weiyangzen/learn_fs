<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/location_test.go -->
# sources/sync-backup/restic/internal/backend/location/location_test.go

## Purpose
Tests repository location parsing and fallback behavior.

## Important APIs, Types, And Functions
testConfig, testFactory, TestParse, TestParseFallback, and TestInvalidScheme are key.

## Control Flow
The tests register a small synthetic factory, parse scheme-prefixed inputs, check local path fallback, and assert invalid schemes fail.

## State And Persistence Behavior
State is a temporary in-memory Registry.

## Dependencies And Integration Points
Depends on location package, backend/location factory constructors, and testing helpers.

## Risks And Edge Cases
The synthetic factory keeps tests focused on parser behavior rather than real backend configs.

## Test Signals
Good unit signal for user-facing repository location parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/location/location_test.go -->
